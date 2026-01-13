"""Main entry point for flux-bootstrap."""

import asyncio
import contextlib
import logging
import multiprocessing
import os
import queue
import shutil
import signal
import sys
import threading
import typing
from importlib.metadata import version
from multiprocessing.synchronize import Event as EventType
from pathlib import Path

import aiohttp
import click
import setproctitle
from rich.console import Console

from flux_bootstrap.cdn_manager import CDNManager
from flux_bootstrap.data_structures import (
    CONNECT_TIMEOUT_SECONDS,
    DEFAULT_API_URL,
    DEFAULT_CDN_URL,
    DIRECT_CDN_URLS,
    MAX_CONCURRENT_DOWNLOADS,
    MAX_UNVERIFIED_PARTS,
    SOCK_READ_TIMEOUT_SECONDS,
)
from flux_bootstrap.download_manager import DownloadManager
from flux_bootstrap.state_manager import StateManager
from flux_bootstrap.worker_processes import (
    sha256_fifo_worker_process,
    tar_extractor_process,
)

# Set multiprocessing start method early (required for async compatibility)
# Must use 'spawn' to avoid issues with forked event loops and file handles
with contextlib.suppress(RuntimeError):
    # Already set (e.g., by tests or parent process)
    multiprocessing.set_start_method("spawn")


def setup_logging(log_file: Path, console: "Console | None" = None) -> None:
    """Setup logging to both console and file.

    Args:
        log_file: Path to log file
        console: Optional rich Console for CLI mode with progress bars
    """

    # Custom formatter to show thread name if not MainThread
    class ProcessThreadFormatter(logging.Formatter):
        def format(self, record):
            # If thread has a meaningful name (not MainThread), use just the thread name
            if record.threadName and record.threadName != "MainThread":
                record.processName = record.threadName
            return super().format(record)

    # Create formatter with timestamp for file/non-rich handlers
    formatter = ProcessThreadFormatter(
        "%(asctime)s [%(processName)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Create formatter without timestamp for RichHandler (it adds its own)
    rich_formatter = ProcessThreadFormatter("[%(processName)s] %(message)s")

    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    # Console handler
    if console is not None:
        # CLI mode with rich progress bars
        from rich.logging import RichHandler

        console_handler = RichHandler(
            console=console,
            show_time=True,
            show_level=False,
            show_path=False,
            markup=False,
            rich_tracebacks=True,
        )
        console_handler.setFormatter(rich_formatter)  # No timestamp in format
    else:
        # Library mode or no progress bars
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)  # Include timestamp

    console_handler.setLevel(logging.INFO)
    root_logger.addHandler(console_handler)

    # File handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)


async def fetch_bootstrap_metadata(api_url: str) -> dict:
    """Fetch bootstrap metadata from API.

    Args:
        api_url: API endpoint URL

    Returns:
        Bootstrap metadata dict
    """
    logging.info(f"Fetching bootstrap metadata from {api_url}")

    async with (
        aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(ssl=False),
            timeout=aiohttp.ClientTimeout(total=30),
        ) as session,
        session.get(api_url) as response,
    ):
        if response.status != 200:
            raise RuntimeError(f"API request failed with status {response.status}")

        data = await response.json()
        if not data:
            raise RuntimeError("No bootstrap data available")

        # Get the latest bootstrap (last key)
        latest_key = max(data.keys())
        return data[latest_key]


async def _download_bootstrap_impl(
    destination: Path,
    parts_dir: Path,
    api_url: str,
    cdn_url: str,
    shutdown_event: EventType,
    *,
    setup_logging_flag: bool = True,
    set_process_title: bool = True,
    progress_callback: typing.Callable[[dict[str, typing.Any]], None] | None = None,
    console: Console | None = None,
    progress_display_ref: list | None = None,
    queue_mark_complete: typing.Callable[[int], None] | None = None,
    queue_verification_slots: typing.Callable[[int, int], None] | None = None,
) -> bool:
    """Internal implementation function for bootstrap download.

    Args:
        destination: Destination directory for extraction
        parts_dir: Directory for storing part files and state
        api_url: API URL for bootstrap metadata
        cdn_url: CDN base URL for downloading bootstrap parts
        shutdown_event: Event to signal shutdown
        setup_logging_flag: Whether to setup logging (default True for CLI)
        set_process_title: Whether to set process title (default True for CLI)
        progress_callback: Optional callback for progress updates (library use)

    Returns:
        True if successful, False otherwise
    """
    if set_process_title:
        setproctitle.setproctitle("flux:boot-dl")

    # Create directories
    destination.mkdir(parents=True, exist_ok=True)
    parts_dir.mkdir(parents=True, exist_ok=True)

    # Setup logging (conditional for library use)
    if setup_logging_flag:
        log_file = parts_dir / "flux-downloader.log"
        setup_logging(log_file, console=console)
        logging.info(f"flux-bootstrap v{version('flux-bootstrap')}")
        logging.info(f"Logging to {log_file}")

    # State manager
    state_file = parts_dir / "state.yaml"
    state_mgr = StateManager(state_file)

    # Load or create state
    state = await state_mgr.load_state()

    if state is None:
        # New download: fetch metadata from API
        metadata = await fetch_bootstrap_metadata(api_url)
        block_height = metadata["block_height"]
        parts = metadata["bootstrap_parts"]

        logging.info(f"Block height: {block_height}")
        logging.info(f"Total parts: {len(parts)}")
        logging.info(
            f"Total size: {sum(p['bytes'] for p in parts) / (1024 * 1024):.1f} MB"
        )

        # Create initial state (all parts unverified)
        state = state_mgr.initialize_state(block_height, cdn_url, parts)
        await state_mgr.save_state(state)
        logging.info("Created new state file")

    else:
        # Resume: state already has all metadata
        logging.info("Resuming download from state file")
        logging.info(f"Block height: {state['block_height']}")
        logging.info(f"Total parts: {len(state['parts'])}")

        # Delete any .part files (incomplete downloads)
        for part_file in parts_dir.glob("*.part"):
            logging.info(f"Deleting incomplete file: {part_file.name}")
            part_file.unlink()

    # Create progress display for CLI mode
    progress_display = None
    if console is not None:
        from flux_bootstrap.progress_display import ProgressDisplay

        total_bytes = sum(p["size"] for p in state["parts"])
        total_parts = len(state["parts"])

        progress_display = ProgressDisplay(console, total_bytes, total_parts)
        progress_display.start()

        # Update reference for callback
        if progress_display_ref is not None:
            progress_display_ref[0] = progress_display

    # Create FIFO
    fifo_path = str(parts_dir / f"bootstrap_fifo_{os.getpid()}.fifo")
    if os.path.exists(fifo_path):
        os.remove(fifo_path)
    os.mkfifo(fifo_path)
    logging.info(f"Created FIFO: {fifo_path}")

    # Create queues (unbounded - backpressure handled by download semaphore)
    notification_queue = multiprocessing.Queue()
    results_queue = multiprocessing.Queue()

    # Start SHA256+FIFO worker process
    worker_proc = multiprocessing.Process(
        target=sha256_fifo_worker_process,
        args=(notification_queue, results_queue, fifo_path, shutdown_event),
    )
    worker_proc.start()
    logging.info("Started SHA256+FIFO worker process")

    # Start tar extractor process
    tar_proc = multiprocessing.Process(
        target=tar_extractor_process,
        args=(fifo_path, destination, shutdown_event),
    )
    tar_proc.start()
    logging.info("Started tar extractor process")

    # Brief delay to let processes open FIFO
    await asyncio.sleep(0.5)

    # Bridge from multiprocessing.Queue to asyncio.Queue
    async_results_queue: asyncio.Queue = asyncio.Queue()

    def queue_bridge_thread():
        """Thread that bridges multiprocessing.Queue (blocking) to asyncio.Queue."""
        logging.debug("[Bridge] Starting bridge thread")
        try:
            while True:
                # Blocking wait for verification result - no log needed
                result = results_queue.get()
                if result is None:  # Poison pill
                    logging.debug("[Bridge] Received shutdown signal")
                    async_results_queue.put_nowait(None)
                    break
                logging.debug(
                    f"[Bridge] Part {result.part_id} verified: {result.verified}"
                )
                async_results_queue.put_nowait(result)
        except Exception as e:
            logging.info(f"Error: {e}")
            import traceback

            logging.info(traceback.format_exc())
            async_results_queue.put_nowait(None)  # Signal async task to exit

    bridge_thread = threading.Thread(
        target=queue_bridge_thread, daemon=True, name="queue-bridge"
    )
    bridge_thread.start()
    logging.info("Bridge thread started")

    # Background task to process verification results
    async def process_verification_results():
        """Background task that reads verification results and updates state."""
        logging.debug("[Results] Starting verification results processor")
        try:
            while not shutdown_event.is_set():
                try:
                    # Poll with timeout to detect unexpected worker death
                    result = await asyncio.wait_for(
                        async_results_queue.get(),
                        timeout=5.0
                    )
                except TimeoutError:
                    # Check if worker died unexpectedly (non-zero exit code)
                    if not worker_proc.is_alive() and worker_proc.exitcode != 0:
                        logging.error(
                            f"Worker process failed "
                            f"(exit code: {worker_proc.exitcode})"
                        )
                        shutdown_event.set()
                        break
                    # Otherwise keep waiting - worker might have finished normally
                    continue

                if result is None:  # Poison pill
                    logging.debug("[Results] Received shutdown signal")
                    break

                # Update state and release verification slot
                if result.verified:
                    await state_mgr.update_part_verified(result.part_id)
                    # Mark part as verified in controller (advances sequential position)
                    await verification_controller.mark_verified(result.part_id)
                    verification_controller.release()

                    logging.info(
                        f"[Verify {result.part_id}] ✓ SHA256 verified "
                        f"({verification_controller.slots_used}/"
                        f"{MAX_UNVERIFIED_PARTS} slots used, "
                        f"next expected: {verification_controller.next_expected_part})"
                    )

                    # Update progress display
                    if progress_display and queue_verification_slots:
                        queue_verification_slots(
                            verification_controller.slots_used, MAX_UNVERIFIED_PARTS
                        )
                else:
                    verification_controller.release()
                    logging.warning(
                        f"[Verify {result.part_id}] ✗ SHA256 verification FAILED - "
                        f"part not marked as verified"
                    )

        except Exception as e:
            logging.error(f"Error processing verification result: {e}")
            import traceback

            logging.error(traceback.format_exc())
        finally:
            logging.debug("[Results] Verification result processor exiting")

    # Start background task
    results_task = asyncio.create_task(process_verification_results())
    logging.info("Started verification results task")

    # Set up Live context for progress display
    if progress_display:
        from rich.live import Live

        live_context = Live(
            progress_display.get_renderable(),
            console=console,
            refresh_per_second=4,
            transient=False,
        )
    else:
        from contextlib import nullcontext

        live_context = nullcontext()

    try:
        with live_context:
            # Sequential verification controller prevents deadlock
            # from out-of-order downloads
            from flux_bootstrap.download_manager import (
                SequentialVerificationController,
            )

            verification_controller = SequentialVerificationController(
                MAX_UNVERIFIED_PARTS
            )

            # CDN manager for failover
            cdn_manager = CDNManager(
                proxy_url=state["cdn_url"],
                direct_urls=DIRECT_CDN_URLS,
            )

            # Calculate totals for progress tracking
            total_bytes = sum(part["size"] for part in state["parts"])
            total_parts = len(state["parts"])

            # Download manager
            download_mgr = DownloadManager(
                cdn_manager,
                parts_dir,
                notification_queue,
                shutdown_event,
                verification_controller,
                total_bytes=total_bytes,
                total_parts=total_parts,
                progress_callback=progress_callback,
            )

            # Emit initial progress event (lets GUIs setup progress bars)
            if progress_callback:
                progress_callback({
                    "bytes_downloaded": 0,
                    "total_bytes": total_bytes,
                    "percent": 0.0,
                    "speed_mbps": 0.0,
                    "cdn_server": None,
                    "served_by": None,
                    "current_part": 1,
                    "total_parts": total_parts,
                    "source": "cdn",
                })

            # Get verified and unverified parts
            verified_parts = state_mgr.get_verified_parts(state)
            first_unverified = state_mgr.get_first_unverified_part(state)

            logging.info(f"Verified parts: {len(verified_parts)}/{len(state['parts'])}")

            # Send verified parts to worker (for streaming to FIFO)
            for part_id in verified_parts:
                if shutdown_event.is_set():
                    break

                part = state["parts"][part_id]
                filepath = parts_dir / f"part_{part_id:04d}.bin"

                success = await download_mgr.stream_verified_part(
                    part_id, filepath, part["sha256"], part["size"]
                )

                # If file missing/invalid, mark as unverified for re-download
                if not success:
                    part["verified"] = False
                    await state_mgr.save_state(state)
                else:
                    # Mark as verified in controller to advance sequential position
                    await verification_controller.mark_verified(part_id)

            # Download unverified parts (iterate through ALL parts to catch any that
            # were marked unverified due to missing files during resume)
            if not shutdown_event.is_set():
                logging.info(f"Starting downloads from part {first_unverified}")

                async with aiohttp.ClientSession(
                    connector=aiohttp.TCPConnector(ssl=False, limit=5),
                    timeout=aiohttp.ClientTimeout(
                        sock_read=SOCK_READ_TIMEOUT_SECONDS,
                        connect=CONNECT_TIMEOUT_SECONDS,
                    ),
                ) as session:
                    # Get list of unverified parts
                    remaining_parts = [
                        part for part in state["parts"]
                        if not part["verified"]
                    ]

                    logging.info(
                        f"Starting downloads: {len(remaining_parts)} parts, "
                        f"{MAX_CONCURRENT_DOWNLOADS} concurrent, "
                        f"{MAX_UNVERIFIED_PARTS}-part verification buffer"
                    )

                    # Download parts with on-demand task creation
                    running_tasks = {}  # task -> part_id mapping
                    failed_parts = []

                    while remaining_parts or running_tasks:
                        # Check for shutdown
                        if shutdown_event.is_set():
                            logging.info("Shutdown requested during downloads")
                            # Cancel all running tasks
                            for task in running_tasks:
                                task.cancel()
                            # Wait for cancellations to complete
                            if running_tasks:
                                await asyncio.wait(running_tasks.keys())
                            break

                        # Fill download slots up to MAX_CONCURRENT_DOWNLOADS
                        while (
                            len(running_tasks) < MAX_CONCURRENT_DOWNLOADS
                            and remaining_parts
                        ):
                            part = remaining_parts.pop(0)
                            task = asyncio.create_task(
                                download_mgr.download_part(
                                    session,
                                    part["id"],
                                    part["path"],
                                    part["sha256"],
                                    part["size"],
                                )
                            )
                            running_tasks[task] = part["id"]
                            logging.debug(
                                f"[Download {part['id']}] Task created "
                                f"({len(running_tasks)} active, "
                                f"{len(remaining_parts)} remaining)"
                            )

                        # Wait for any task to complete
                        if running_tasks:
                            done, pending = await asyncio.wait(
                                running_tasks.keys(),
                                return_when=asyncio.FIRST_COMPLETED,
                                timeout=1.0  # Check shutdown periodically
                            )

                            # Process completed tasks
                            for task in done:
                                part_id = running_tasks.pop(task)

                                try:
                                    # Get boolean return value
                                    success = task.result()

                                    if not success:
                                        # Download failed after all CDN attempts
                                        logging.error(
                                            f"[Download {part_id}] Failed after all "
                                            f"retry attempts"
                                        )
                                        failed_parts.append(part_id)

                                        # Trigger immediate shutdown
                                        logging.info(
                                            f"Setting shutdown event due to "
                                            f"part {part_id} failure"
                                        )
                                        shutdown_event.set()

                                        # Cancel all remaining running tasks
                                        tasks_to_cancel = list(running_tasks)
                                        for cancel_task in tasks_to_cancel:
                                            cancel_task.cancel()

                                        # Await all cancellations
                                        for cancel_task in tasks_to_cancel:
                                            with contextlib.suppress(
                                                asyncio.CancelledError
                                            ):
                                                await cancel_task

                                        running_tasks.clear()
                                    else:
                                        # Download succeeded
                                        logging.debug(
                                            f"[Download {part_id}] Completed "
                                            f"successfully"
                                        )

                                        # Update progress display
                                        if progress_display and queue_mark_complete:
                                            download_mgr.cleanup_part_tracking(part_id)
                                            queue_mark_complete(part_id)

                                except asyncio.CancelledError:
                                    # Task was cancelled during shutdown
                                    logging.info(f"[Download {part_id}] Task cancelled")
                                    # Expected during shutdown

                                except Exception as e:
                                    # Unexpected exception from download_part()
                                    logging.error(
                                        f"[Download {part_id}] Unexpected exception: "
                                        f"{type(e).__name__}: {e}"
                                    )
                                    failed_parts.append(part_id)

                    # Report final results
                    if shutdown_event.is_set():
                        # Shutdown was requested - don't treat as fatal error
                        logging.info("Download interrupted by shutdown")
                    elif failed_parts:
                        # Some downloads failed
                        logging.info(
                            f"FATAL: {len(failed_parts)} parts failed to download "
                            f"after all retry attempts"
                        )
                        logging.info(
                            "Download incomplete. State and successfully downloaded "
                            "parts preserved."
                        )
                        logging.info("Run again to resume from current state.")
                        # Set shutdown event and exit
                        shutdown_event.set()
                        # Continue to cleanup section
                        return False
                    else:
                        # All downloads succeeded
                        total_parts = len(state["parts"])
                        total_size_mb = (
                            sum(p["size"] for p in state["parts"]) / (1024 * 1024)
                        )
                        logging.info(
                            f"All {total_parts} parts downloaded successfully "
                            f"({total_size_mb:.1f} MB total)"
                        )

            # Signal worker to stop accepting new parts
            notification_queue.put(None)
            logging.debug("[Shutdown] Sent shutdown signal to worker")

            # If graceful completion, wait for worker to finish all buffered parts
            # If interrupted (Ctrl+C), terminate immediately
            if not shutdown_event.is_set():
                # Graceful completion - wait for worker to finish verifying parts
                logging.debug(
                    "[Shutdown] Waiting for worker to finish "
                    "processing buffered parts..."
                )
                worker_proc.join(timeout=120)
                if worker_proc.is_alive():
                    logging.warning(
                        "[Shutdown] Worker process did not finish in time, "
                        "terminating..."
                    )
                    worker_proc.terminate()
                    worker_proc.join()
                logging.debug("[Shutdown] Worker finished")

                # Now that worker finished, all verification results have been sent
                # Wait a bit for results to propagate through the queues
                await asyncio.sleep(0.5)

                # Signal results processor to finish
                logging.debug("[Shutdown] Sending poison pill to results processor")
                results_queue.put(None)
                try:
                    await asyncio.wait_for(results_task, timeout=5.0)
                except TimeoutError:
                    logging.debug("[Shutdown] Results task timed out, cancelling...")
                    results_task.cancel()
                    with contextlib.suppress(asyncio.CancelledError):
                        await results_task
                logging.debug("[Shutdown] Results processor finished")
            else:
                # Interrupted - terminate worker immediately
                logging.info("Interrupted - terminating worker immediately")
                if worker_proc.is_alive():
                    worker_proc.terminate()
                    worker_proc.join(timeout=2)

                # Signal and terminate results processor
                results_queue.put(None)
                results_task.cancel()
                with contextlib.suppress(asyncio.CancelledError):
                    await results_task

            # Wait for tar extractor
            total_parts = len(state["parts"])
            logging.info(
                f"All {total_parts} parts verified. Extracting to {destination}..."
            )

            if progress_display:
                progress_display.show_extraction_status()

            tar_proc.join(timeout=60)
            if tar_proc.is_alive():
                logging.info("Tar extractor did not finish, terminating...")
                tar_proc.terminate()
                tar_proc.join()
                return False

            extraction_success = tar_proc.exitcode == 0
            if extraction_success:
                logging.info("✓ Tar extraction completed successfully")
                logging.info("✓ Bootstrap installation complete")

                # Clean up bootstrap_parts directory
                with contextlib.suppress(Exception):
                    logging.info(f"Deleting bootstrap_parts directory: {parts_dir}")
                    shutil.rmtree(parts_dir)
                    logging.info("Bootstrap parts cleaned up successfully")
            else:
                logging.error(
                    f"✗ Tar extraction failed (exit code: {tar_proc.exitcode})"
                )

            return extraction_success

    except KeyboardInterrupt:
        logging.info("\nInterrupted by user")
        return False

    except Exception as e:
        logging.info(f"Error: {e}")
        import traceback

        traceback.print_exc()
        return False

    finally:
        # Cleanup
        logging.info("Cleaning up...")

        # Signal bridge thread and results task to exit
        with contextlib.suppress(Exception):
            results_queue.put(None)  # Send poison pill to bridge thread

        # Cancel results task if still running
        if not results_task.done():
            results_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await results_task

        # Wait for bridge thread to exit
        if bridge_thread.is_alive():
            bridge_thread.join(timeout=2.0)

        # Terminate processes if still running
        if worker_proc.is_alive():
            worker_proc.terminate()
            worker_proc.join(timeout=2)

        if tar_proc.is_alive():
            tar_proc.terminate()
            tar_proc.join(timeout=2)

        # Cleanup FIFO
        try:
            if os.path.exists(fifo_path):
                os.remove(fifo_path)
                logging.info("Cleaned up FIFO")
        except OSError:
            pass


async def async_main(
    destination: Path,
    parts_dir: Path,
    api_url: str,
    cdn_url: str,
    shutdown_event: EventType,
    no_progress: bool = False,
) -> bool:
    """CLI entry point - calls implementation with CLI defaults.

    Args:
        destination: Destination directory for extraction
        parts_dir: Directory for storing part files and state
        api_url: API URL for bootstrap metadata
        cdn_url: CDN base URL for downloading bootstrap parts
        shutdown_event: Event to signal shutdown
        no_progress: Disable progress bars (use plain logging)

    Returns:
        True if successful, False otherwise
    """
    # Create Rich console for CLI (disabled if --no-progress flag set)
    console = None if no_progress else Console()

    # Progress display will be created after metadata fetch
    # Using list for mutability in callback closure
    progress_display_ref = [None]

    # Queue for progress updates (to avoid blocking downloads on Rich's lock)
    progress_queue: queue.Queue | None = None
    progress_thread: threading.Thread | None = None

    if console is not None:
        progress_queue = queue.Queue()

        def progress_update_worker():
            """Thread that reads progress updates and calls Rich.

            Blocking I/O isolated from main event loop.
            """
            while True:
                try:
                    data = progress_queue.get(timeout=1.0)
                    if data is None:  # Poison pill
                        break
                    if not progress_display_ref[0]:
                        continue

                    # Handle different update types
                    update_type = data.get("type")
                    if update_type == "progress":
                        progress_display_ref[0].update_from_callback(data)
                    elif update_type == "mark_complete":
                        progress_display_ref[0].mark_part_complete(data["part_id"])
                    elif update_type == "verification_slots":
                        progress_display_ref[0].update_verification_slots(
                            data["used"], data["total"]
                        )
                except queue.Empty:
                    continue

        progress_thread = threading.Thread(
            target=progress_update_worker, daemon=True, name="progress-update"
        )
        progress_thread.start()

    def progress_callback(data: dict) -> None:
        """Progress callback that queues updates (non-blocking)."""
        if progress_queue:
            data["type"] = "progress"
            progress_queue.put_nowait(data)

    def queue_mark_complete(part_id: int) -> None:
        """Queue mark complete operation (non-blocking)."""
        if progress_queue:
            progress_queue.put_nowait({"type": "mark_complete", "part_id": part_id})

    def queue_verification_slots(used: int, total: int) -> None:
        """Queue verification slots update (non-blocking)."""
        if progress_queue:
            progress_queue.put_nowait(
                {"type": "verification_slots", "used": used, "total": total}
            )

    try:
        return await _download_bootstrap_impl(
            destination=destination,
            parts_dir=parts_dir,
            api_url=api_url,
            cdn_url=cdn_url,
            shutdown_event=shutdown_event,
            setup_logging_flag=True,
            set_process_title=True,
            progress_callback=progress_callback,
            console=console,
            progress_display_ref=progress_display_ref,
            queue_mark_complete=queue_mark_complete,
            queue_verification_slots=queue_verification_slots,
        )
    finally:
        # Shutdown progress update thread
        if progress_queue is not None:
            progress_queue.put(None)  # Poison pill
        if progress_thread is not None and progress_thread.is_alive():
            progress_thread.join(timeout=2.0)


@click.command()
@click.version_option(version=version("flux-bootstrap"), prog_name="flux-bootstrap")
@click.argument("destination", type=click.Path(file_okay=False, path_type=Path))
@click.option(
    "--api-url",
    default=DEFAULT_API_URL,
    help="API URL for bootstrap metadata",
    show_default=True,
)
@click.option(
    "--cdn-url",
    default=DEFAULT_CDN_URL,
    help="CDN base URL for downloading bootstrap parts",
    show_default=True,
)
@click.option(
    "--no-progress",
    is_flag=True,
    help="Disable progress bars (use plain logging)",
)
def run(destination: Path, api_url: str, cdn_url: str, no_progress: bool) -> None:
    """Download and extract Flux blockchain bootstrap files.

    DESTINATION: Directory where blockchain data will be extracted
    """
    destination = destination.resolve()
    # Parts directory is internal implementation detail
    parts_dir = destination / "bootstrap_parts"

    # Shutdown event
    shutdown_event = multiprocessing.Event()

    # Signal handler
    def signal_handler(_sig, _frame):
        logging.info("Shutdown requested...")
        shutdown_event.set()

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGHUP, signal_handler)

    try:
        success = asyncio.run(
            async_main(
                destination, parts_dir, api_url, cdn_url, shutdown_event, no_progress
            )
        )
        sys.exit(0 if success else 1)

    except KeyboardInterrupt:
        logging.info("\nInterrupted by user")
        sys.exit(130)

    except Exception as e:
        logging.info(f"Fatal error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    run()

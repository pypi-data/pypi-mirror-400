"""Worker processes for SHA256 verification, FIFO writing, and tar extraction."""

import hashlib
import logging
import multiprocessing
import os
import signal
import sys
import tarfile
from multiprocessing.synchronize import Event as EventType
from pathlib import Path
from queue import Empty

import setproctitle

from flux_bootstrap.data_structures import FIFO_CHUNK_SIZE, VerificationResult


def sha256_fifo_worker_process(
    notification_queue: multiprocessing.Queue,
    results_queue: multiprocessing.Queue,
    fifo_path: str,
    shutdown_event: EventType,
) -> None:
    """Worker process that verifies SHA256 and streams to FIFO.

    Combined pattern from v4's fifo_writer_process:
    - Receives PartNotification messages
    - Reads parts from disk, computes SHA256
    - Buffers out-of-order parts
    - Writes to FIFO sequentially
    - Sends verification results back to main process

    Args:
        notification_queue: Queue receiving PartNotification objects
        results_queue: Queue for sending VerificationResult objects to main
        fifo_path: Path to FIFO pipe
        shutdown_event: Event to signal shutdown
    """
    multiprocessing.current_process().name = "flux:boot-sha"
    setproctitle.setproctitle("flux:boot-sha")
    signal.signal(signal.SIGINT, signal.SIG_IGN)  # Ignore Ctrl+C

    # Track parent process to detect if it dies
    parent_pid = os.getppid()

    try:
        # Track which parts we have ready
        buffered_parts = {}  # {part_id: (filepath, expected_sha256, size)}
        current_part = 0  # Next part to write to FIFO

        logging.info(f"Opening FIFO: {fifo_path}")
        with open(fifo_path, "wb") as fifo:
            logging.info("FIFO opened, ready to process parts")

            while not shutdown_event.is_set():
                # Check if parent process died (exit if orphaned)
                if os.getppid() != parent_pid:
                    logging.info("Parent process died, worker exiting")
                    break

                try:
                    # Get notification (timeout to check parent and shutdown_event)
                    msg = notification_queue.get(timeout=5.0)

                    if msg is None:  # Poison pill
                        logging.info("Received shutdown signal")
                        break

                    # Buffer this part
                    buffered_parts[msg.part_id] = (
                        msg.filepath,
                        msg.expected_sha256,
                        msg.size,
                        msg.already_verified,
                    )
                    logging.info(
                        f"Buffered part {msg.part_id}, waiting for part {current_part}"
                    )

                    # Process parts in sequential order
                    while current_part in buffered_parts:
                        filepath, expected_sha256, size, already_verified = (
                            buffered_parts.pop(current_part)
                        )

                        logging.info(f"Processing part {current_part}")

                        if already_verified:
                            # Resume: just stream to FIFO, skip SHA256
                            total_written = 0
                            with open(filepath, "rb") as part_file:
                                while True:
                                    chunk = part_file.read(FIFO_CHUNK_SIZE)
                                    if not chunk:
                                        break
                                    fifo.write(chunk)
                                    total_written += len(chunk)
                                fifo.flush()

                            logging.info(
                                f"Part {current_part} streamed "
                                f"(already verified, {total_written} bytes)"
                            )
                        else:
                            # New download: compute SHA256, stream to FIFO
                            sha256_hash = hashlib.sha256()
                            total_written = 0

                            with open(filepath, "rb") as part_file:
                                while True:
                                    chunk = part_file.read(FIFO_CHUNK_SIZE)
                                    if not chunk:
                                        break

                                    # Update SHA256
                                    sha256_hash.update(chunk)

                                    # Write to FIFO
                                    fifo.write(chunk)
                                    total_written += len(chunk)

                                # Flush after each part
                                fifo.flush()

                            # Verify SHA256
                            actual_sha256 = sha256_hash.hexdigest()
                            verified = actual_sha256 == expected_sha256

                            if verified:
                                logging.info(
                                    f"Part {current_part} verified "
                                    f"({total_written} bytes)"
                                )
                            else:
                                logging.info(f"Part {current_part} SHA256 MISMATCH!")
                                logging.info(f"  Expected: {expected_sha256}")
                                logging.info(f"  Actual:   {actual_sha256}")

                            # Send verification result to main process
                            result = VerificationResult(
                                part_id=current_part,
                                verified=verified,
                                actual_sha256=actual_sha256,
                            )
                            logging.info(
                                f"Sending result to queue for part {current_part}"
                            )
                            try:
                                results_queue.put(result, timeout=1.0)
                                logging.info(
                                    f"Successfully sent result for part {current_part}"
                                )
                            except Exception as e:
                                logging.info(f"Failed to send result: {e}")

                        current_part += 1

                except Empty:
                    continue
                except Exception as e:
                    logging.info(f"Error: {e}")
                    import traceback

                    traceback.print_exc()
                    break

        logging.info("Exiting")

    except Exception as e:
        logging.info(f"Fatal error: {e}")
        import traceback

        traceback.print_exc()


def tar_extractor_process(
    fifo_path: str, destination: Path, _stop_event: EventType
) -> None:
    """Extract tar from FIFO to destination.

    Pattern from test_concurrent_bootstrap.py extraction_process:
    - Opens FIFO as file object
    - Creates streaming tarfile reader
    - Extracts all to destination

    Args:
        fifo_path: Path to FIFO pipe
        destination: Destination directory for extraction
        stop_event: Event to signal stop (not currently used but matches pattern)
    """
    multiprocessing.current_process().name = "flux:boot-tar"
    setproctitle.setproctitle("flux:boot-tar")
    signal.signal(signal.SIGINT, signal.SIG_IGN)  # Ignore Ctrl+C

    try:
        logging.info(f"Opening FIFO: {fifo_path}")
        with open(fifo_path, "rb") as fifo:
            logging.info(f"FIFO opened, starting tar extraction to {destination}")

            with tarfile.open(mode="r|*", fileobj=fifo, stream=True) as tar:  # type: ignore[call-overload]
                # Use 'data' filter for secure extraction (Python 3.12+)
                tar.extractall(path=destination, filter="data")

        logging.info("Extraction completed successfully")
        sys.exit(0)

    except tarfile.ReadError as e:
        logging.info(f"Tar extraction stopped: {e}")
        sys.exit(1)
    except Exception as e:
        logging.info(f"Error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)

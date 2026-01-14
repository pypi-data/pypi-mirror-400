"""Download management for concurrent part downloads."""

import asyncio
import logging
import multiprocessing
import time
import typing
from multiprocessing.synchronize import Event as EventType
from pathlib import Path
from urllib.parse import urlparse

import aiofiles
import aiohttp

from flux_bootstrap.cdn_manager import CDNManager, SlowDownloadError
from flux_bootstrap.data_structures import (
    DOWNLOAD_CHUNK_SIZE,
    MIN_SPEED_MBPS,
    RETRY_DELAY_SECONDS,
    SPEED_CHECK_WINDOW_SECONDS,
    PartNotification,
)
from flux_bootstrap.speed_monitor import SpeedMonitor


class SequentialVerificationController:
    """Controls verification to prevent deadlock from out-of-order downloads.

    Enforces that downloads can't get more than MAX_UNVERIFIED_PARTS ahead
    of the current sequential processing position.
    """

    def __init__(self, max_unverified: int):
        self.next_expected_part = 0  # Next part worker is waiting to process
        self.verified_parts: set[int] = set()  # Parts verified but not yet sequential
        self.condition = asyncio.Condition()
        self.semaphore = asyncio.Semaphore(max_unverified)
        self.max_unverified = max_unverified
        self.slots_used = 0  # Track slots currently in use

    async def acquire_for_part(self, part_id: int) -> None:
        """Acquire slot for part, waiting if too far ahead sequentially.

        Args:
            part_id: Part number (0-indexed)
        """
        # Wait until this part is within MAX_UNVERIFIED_PARTS of next expected
        async with self.condition:
            while part_id >= self.next_expected_part + self.max_unverified:
                logging.debug(
                    f"[Download {part_id}] Waiting - too far ahead "
                    f"(next expected: {self.next_expected_part}, "
                    f"max distance: {self.max_unverified})"
                )
                await self.condition.wait()

        # Acquire semaphore slot
        await self.semaphore.acquire()
        self.slots_used += 1
        logging.debug(
            f"[Download {part_id}] Acquired verification slot "
            f"({self.slots_used}/{self.max_unverified} used)"
        )

    def release(self) -> None:
        """Release semaphore slot."""
        self.slots_used -= 1
        self.semaphore.release()

    async def mark_verified(self, part_id: int) -> None:
        """Mark part as verified and advance sequential position if possible.

        Args:
            part_id: Part number (0-indexed)
        """
        async with self.condition:
            self.verified_parts.add(part_id)

            # Advance next_expected_part while we have sequential parts
            while self.next_expected_part in self.verified_parts:
                self.verified_parts.remove(self.next_expected_part)
                self.next_expected_part += 1

            # Wake up any downloads waiting for sequential position to advance
            self.condition.notify_all()


class DownloadManager:
    """Manages concurrent downloads of bootstrap parts."""

    def __init__(
        self,
        cdn_manager: CDNManager,
        parts_dir: Path,
        notification_queue: multiprocessing.Queue,
        shutdown_event: EventType,
        verification_controller: SequentialVerificationController,
        total_bytes: int = 0,
        total_parts: int = 0,
        progress_callback: typing.Callable[[dict[str, typing.Any]], None] | None = None,
        progress_interval: float = 1.0,
        part_started_callback: typing.Callable[[int, int], None] | None = None,
        bytes_already_downloaded: int = 0,
    ):
        self.cdn_manager = cdn_manager
        self.parts_dir = parts_dir
        self.notification_queue = notification_queue
        self.shutdown_event = shutdown_event
        self.verification_controller = verification_controller

        # Progress tracking for library API
        self.progress_callback = progress_callback
        self._total_bytes = total_bytes
        # Initialize with verified bytes on resume
        self._bytes_downloaded = bytes_already_downloaded
        self._total_parts = total_parts
        self._progress_interval = progress_interval  # Progress callback interval (sec)
        self._last_progress_emit = 0.0  # Timestamp of last progress emission
        # Start baseline at verified bytes
        self._last_progress_bytes = bytes_already_downloaded
        self._current_cdn_url: str | None = None  # Track current CDN for progress
        self._current_served_by: str | None = None  # Track x-served-by header

        # Lifecycle callbacks
        self.part_started_callback = part_started_callback

        # Per-part tracking for progress UI
        self._part_sizes: dict[int, int] = {}
        self._part_bytes_downloaded: dict[int, int] = {}
        self._last_part_bytes: dict[int, int] = {}  # Per-part bytes at last emission

    async def download_part(
        self,
        session: aiohttp.ClientSession,
        part_id: int,
        part_path: str,
        size: int,
    ) -> bool:
        """Download a single part to disk with CDN failover.

        Implements 2+1+1+1 strategy: 2 attempts on proxy, then 1 attempt each
        on 3 direct backend CDNs (max 5 total attempts).

        Args:
            session: aiohttp session
            part_id: Part number
            part_path: Relative path on CDN
            size: Expected size in bytes

        Returns:
            True if download succeeded, False if all CDN attempts failed
        """
        # Create failover strategy for this part
        strategy = self.cdn_manager.create_failover_strategy()

        attempt_count = 0

        while True:
            if self.shutdown_event.is_set():
                return False

            # Get next CDN to try
            cdn_url, cdn_attempt, max_cdn_attempts = strategy.get_next_cdn()

            if cdn_url is None:
                # All CDNs exhausted
                logging.error(
                    f"[Download {part_id}] All CDN attempts failed "
                    f"(total: {attempt_count})"
                )
                return False

            attempt_count += 1

            # Log which CDN we're trying
            logging.info(
                f"[Download {part_id}] Trying CDN: {cdn_url} "
                f"(attempt {cdn_attempt}/{max_cdn_attempts}, "
                f"{strategy.get_phase_summary()})"
            )

            # Add delay before retry (but not on first attempt)
            if attempt_count > 1:
                await asyncio.sleep(RETRY_DELAY_SECONDS)

            # Create speed monitor for this attempt
            speed_monitor = SpeedMonitor(
                threshold_mbps=MIN_SPEED_MBPS,
                check_window_seconds=SPEED_CHECK_WINDOW_SECONDS,
            )

            # Try download with this CDN
            success, served_by_header = await self._download_part_once(
                session, part_id, part_path, size, cdn_url, speed_monitor
            )

            if success:
                logging.info(
                    f"[Download {part_id}] Successfully downloaded "
                    f"from {cdn_url}"
                )
                return True

            # Record failure in strategy
            failure_reason = f"Download failed (attempt {cdn_attempt})"
            strategy.record_failure(served_by_header, failure_reason)

    async def _download_part_once(
        self,
        session: aiohttp.ClientSession,
        part_id: int,
        part_path: str,
        size: int,
        cdn_url: str,
        speed_monitor: SpeedMonitor,
    ) -> tuple[bool, str | None]:
        """Download a single part to disk (single attempt).

        Pure IO operation - streams from network to disk.
        NO CPU work (no SHA256, no processing).

        Monitors download speed and raises SlowDownloadError if too slow.

        Args:
            session: aiohttp session
            part_id: Part number
            part_path: Relative path on CDN
            expected_sha256: Expected SHA256 (for notification only)
            size: Expected size in bytes
            cdn_url: CDN base URL to use for this attempt
            speed_monitor: Speed monitor for this attempt

        Returns:
            Tuple of (success, served_by_header)
            - success: True if download succeeded, False otherwise
            - served_by_header: Value of x-served-by header (or None)
        """
        if self.shutdown_event.is_set():
            return (False, None)

        url = f"{cdn_url}/{part_path}"
        filepath = self.parts_dir / f"part_{part_id:04d}.bin"

        # Track current CDN URL for progress reporting
        self._current_cdn_url = cdn_url

        # Initialize part tracking for progress UI
        self._part_sizes[part_id] = size
        self._part_bytes_downloaded[part_id] = 0

        # Notify UI that part started (for immediate progress bar creation)
        if self.part_started_callback:
            self.part_started_callback(part_id, size)

        logging.info(f"[Download {part_id}] Starting download from {url}")

        try:
            async with session.get(url) as response:
                # Extract x-served-by header for CDN identification
                served_by = response.headers.get("x-served-by")
                if served_by:
                    self._current_served_by = served_by
                    logging.debug(
                        f"[Download {part_id}] Served by: {served_by}"
                    )

                if response.status != 200:
                    logging.info(
                        f"[Download {part_id}] HTTP {response.status}: "
                        f"{response.reason}"
                    )
                    return (False, served_by)

                # Stream directly to disk (pure IO, no CPU work)
                bytes_downloaded = 0
                async with aiofiles.open(filepath, "wb") as f:
                    async for chunk in response.content.iter_chunked(
                        DOWNLOAD_CHUNK_SIZE
                    ):
                        await f.write(chunk)
                        bytes_downloaded += len(chunk)

                        # Update global progress tracking
                        self._bytes_downloaded += len(chunk)

                        # Update per-part tracking
                        self._part_bytes_downloaded[part_id] = bytes_downloaded

                        # Record chunk for speed monitoring
                        speed_monitor.record_chunk(len(chunk))

                        # Check if download is too slow
                        if speed_monitor.is_too_slow():
                            current_speed = speed_monitor.get_current_speed_mbps()
                            elapsed = speed_monitor.get_elapsed_time()
                            logging.warning(
                                f"[Download {part_id}] Speed too slow: "
                                f"{current_speed:.2f} Mbps < {MIN_SPEED_MBPS} Mbps "
                                f"for {elapsed:.0f}s. Aborting."
                            )
                            # Delete incomplete file
                            if filepath.exists():
                                filepath.unlink()
                            raise SlowDownloadError(current_speed, served_by)

                        # Check for shutdown
                        if self.shutdown_event.is_set():
                            logging.info(
                                f"[Download {part_id}] Cancelled by shutdown event"
                            )
                            # Delete incomplete file
                            if filepath.exists():
                                filepath.unlink()
                            return (False, served_by)

            mb_downloaded = bytes_downloaded / (1024 * 1024)
            current_speed = speed_monitor.get_current_speed_mbps()
            logging.info(
                f"[Download {part_id}] Downloaded {mb_downloaded:.1f} MB "
                f"(avg speed: {current_speed:.2f} Mbps)"
            )

            return (True, served_by)

        except SlowDownloadError as e:
            # Already logged in the check above
            return (False, e.served_by)

        except aiohttp.ClientResponseError as e:
            logging.warning(
                f"[Download {part_id}] HTTP {e.status}: {e.message} "
                f"(will retry with next CDN)"
            )
            if filepath.exists():
                filepath.unlink()
            return (False, None)

        except aiohttp.ClientPayloadError:
            # Includes ContentLengthError
            logging.warning(
                f"[Download {part_id}] Incomplete download: "
                f"connection closed or payload mismatch (will retry with next CDN)"
            )
            if filepath.exists():
                filepath.unlink()
            return (False, None)

        except aiohttp.ClientError as e:
            # Catch-all for other aiohttp errors
            error_type = type(e).__name__
            logging.warning(
                f"[Download {part_id}] {error_type}: {e} "
                f"(will retry with next CDN)"
            )
            if filepath.exists():
                filepath.unlink()
            return (False, None)

        except Exception as e:
            error_type = type(e).__name__
            logging.error(
                f"[Download {part_id}] Unexpected {error_type}: {e}"
            )
            if filepath.exists():
                filepath.unlink()
            return (False, None)

    async def send_notification(
        self,
        part_id: int,
        filepath: Path,
        expected_sha256: str,
        size: int,
        already_verified: bool = False,
    ) -> None:
        """Send notification to worker that part is ready.

        Acquires verification slot before sending, enforcing sequential distance limit.

        Args:
            part_id: Part number
            filepath: Path to downloaded file
            expected_sha256: Expected SHA256 checksum
            size: File size in bytes
            already_verified: True if part already verified (resume scenario)
        """
        # Acquire slot in verification queue (limits unverified parts)
        # Only for new downloads - already verified parts bypass limit
        if not already_verified:
            try:
                await self.verification_controller.acquire_for_part(part_id)
            except asyncio.CancelledError:
                # Task was cancelled while waiting for verification slot
                logging.info(
                    f"[Download {part_id}] Cancelled while waiting for "
                    f"verification slot"
                )
                raise  # Re-raise so task completes as cancelled

        notification = PartNotification(
            part_id=part_id,
            filepath=str(filepath),
            expected_sha256=expected_sha256,
            size=size,
            already_verified=already_verified,
        )

        try:
            self.notification_queue.put(notification, timeout=1.0)
            log_type = "Resume" if already_verified else "Download"
            logging.debug(f"[{log_type} {part_id}] Sent notification to worker")
        except Exception as e:
            logging.warning(f"[Download {part_id}] Failed to send notification: {e}")
            # Release semaphore on failure
            if not already_verified:
                self.verification_controller.release()

    async def stream_verified_part(
        self, part_id: int, filepath: Path, expected_sha256: str, size: int
    ) -> bool:
        """Send notification for already-verified part (resume scenario).

        For resume: part is already on disk and verified.
        Just send notification to worker to stream to FIFO.

        Args:
            part_id: Part number
            filepath: Path to verified file
            expected_sha256: Expected SHA256
            size: File size

        Returns:
            True if part sent successfully, False if file missing/invalid
        """
        # Verify file actually exists before sending to worker
        if not filepath.exists():
            logging.warning(
                f"[Resume {part_id}] Part marked as verified but file missing: "
                f"{filepath}. Will re-download."
            )
            return False

        # Verify file size matches expected
        actual_size = filepath.stat().st_size
        if actual_size != size:
            logging.warning(
                f"[Resume {part_id}] Part file size mismatch "
                f"(expected {size}, got {actual_size}). Will re-download."
            )
            return False

        logging.info(f"[Resume {part_id}] Sending verified part to worker")
        await self.send_notification(
            part_id, filepath, expected_sha256, size, already_verified=True
        )
        return True

    def _extract_hostname(self, url: str) -> str:
        """Extract hostname from CDN URL."""
        parsed = urlparse(url)
        return parsed.netloc or url

    def emit_aggregate_progress(self) -> None:
        """Emit single progress callback with ALL active parts.

        Called by central periodic timer. Samples all counters at once,
        calculates speeds using same time delta, guaranteeing sum of
        parts equals aggregate.
        """
        if not self.progress_callback:
            return

        now = time.perf_counter()
        time_delta = now - self._last_progress_emit

        if time_delta <= 0:
            return  # No time has passed

        # Calculate aggregate speed
        bytes_delta = self._bytes_downloaded - self._last_progress_bytes
        aggregate_speed = (bytes_delta / time_delta * 8) / 1_000_000

        # Build parts array with synchronized speeds
        parts = []
        for part_id, current_bytes in self._part_bytes_downloaded.items():
            last_bytes = self._last_part_bytes.get(part_id, 0)
            part_delta = current_bytes - last_bytes
            part_speed = (part_delta / time_delta * 8) / 1_000_000

            parts.append({
                "part_id": part_id,
                "bytes_downloaded": current_bytes,
                "total_bytes": self._part_sizes.get(part_id, 0),
                "speed_mbps": part_speed,
            })

            # Update baseline for next measurement
            self._last_part_bytes[part_id] = current_bytes

        # Update global baselines
        self._last_progress_emit = now
        self._last_progress_bytes = self._bytes_downloaded

        # Calculate overall percent
        percent = 0.0
        if self._total_bytes > 0:
            percent = (self._bytes_downloaded / self._total_bytes) * 100.0

        # Get CDN info
        cdn_server = None
        if self._current_cdn_url:
            cdn_server = self._extract_hostname(self._current_cdn_url)

        # Emit SINGLE callback with all parts
        progress_data = {
            "bytes_downloaded": self._bytes_downloaded,
            "total_bytes": self._total_bytes,
            "percent": percent,
            "speed_mbps": aggregate_speed,
            "cdn_server": cdn_server,
            "served_by": self._current_served_by,
            "total_parts": self._total_parts,
            "source": "cdn",
            "parts": parts,  # Array of all active parts
        }

        self.progress_callback(progress_data)

    def cleanup_part_tracking(self, part_id: int) -> None:
        """Clean up tracking data for completed part.

        Args:
            part_id: Part number (0-indexed)
        """
        self._part_sizes.pop(part_id, None)
        self._part_bytes_downloaded.pop(part_id, None)
        self._last_part_bytes.pop(part_id, None)

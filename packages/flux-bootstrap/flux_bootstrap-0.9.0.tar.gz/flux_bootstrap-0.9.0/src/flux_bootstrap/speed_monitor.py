"""
Download speed monitoring for CDN failover decisions.

Monitors download speed over a rolling time window to detect slow connections
that should trigger CDN failover.
"""

import time


class SpeedMonitor:
    """
    Monitors download speed over a time window.

    Tracks bytes downloaded and calculates speed to detect connections
    that are too slow (< threshold for full window duration).
    """

    def __init__(
        self,
        threshold_mbps: float = 1.0,
        check_window_seconds: int = 120,
    ) -> None:
        """
        Initialize speed monitor.

        Args:
            threshold_mbps: Minimum acceptable speed in megabits per second
            check_window_seconds: Time window to measure speed (default 2 minutes)
        """
        self.threshold_mbps = threshold_mbps
        # Convert Mbps to bytes per second
        # (1 Mbps = 1,000,000 bits/s ÷ 8 = 125,000 bytes/s)
        self.threshold_bytes_per_sec = threshold_mbps * 1_000_000 / 8
        self.check_window = check_window_seconds

        # Timing
        self.start_time = time.monotonic()
        self.window_start: float | None = None

        # Byte tracking
        self.window_bytes = 0

    def record_chunk(self, num_bytes: int) -> None:
        """
        Record bytes downloaded.

        Args:
            num_bytes: Number of bytes in this chunk
        """
        now = time.monotonic()

        # Initialize window on first chunk
        if self.window_start is None:
            self.window_start = now

        self.window_bytes += num_bytes

    def is_too_slow(self) -> bool:
        """
        Check if download speed is below threshold for the full window.

        Returns:
            True if speed has been below threshold for full check_window duration
        """
        if self.window_start is None:
            return False  # No data yet

        elapsed = time.monotonic() - self.window_start

        # Don't fail until we have a full window of data
        if elapsed < self.check_window:
            return False

        # Calculate average speed over the window
        speed_bytes_per_sec = self.window_bytes / elapsed

        return speed_bytes_per_sec < self.threshold_bytes_per_sec

    def get_current_speed_mbps(self) -> float:
        """
        Get current download speed in megabits per second.

        Returns:
            Current speed in Mbps, or 0.0 if no data yet
        """
        if self.window_start is None:
            return 0.0

        elapsed = time.monotonic() - self.window_start
        if elapsed == 0:
            return 0.0

        # Calculate speed in bytes/sec, then convert to Mbps
        speed_bytes_per_sec = self.window_bytes / elapsed
        speed_mbps = (speed_bytes_per_sec * 8) / 1_000_000

        return speed_mbps

    def get_elapsed_time(self) -> float:
        """
        Get elapsed time since first chunk.

        Returns:
            Elapsed seconds, or 0.0 if no data yet
        """
        if self.window_start is None:
            return 0.0
        return time.monotonic() - self.window_start

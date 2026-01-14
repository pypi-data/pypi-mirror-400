"""Data structures and constants for flux-downloader."""

from dataclasses import dataclass

# Download and streaming constants
DOWNLOAD_CHUNK_SIZE = 16 * 1024 * 1024  # 16MB chunks for network reads
WRITE_BUFFER_CHUNKS = 2  # Chunks to buffer before back-pressure (2 * 16MB = 32MB)
FIFO_CHUNK_SIZE = 64 * 1024  # 64KB chunks for FIFO writing (tar needs smaller chunks)
MAX_CONCURRENT_DOWNLOADS = 2  # Max concurrent part downloads
MAX_DOWNLOAD_ATTEMPTS = 3  # Max attempts per download (1 initial + 2 retries)
RETRY_DELAY_SECONDS = 1  # Delay between retry attempts
MAX_UNVERIFIED_PARTS = 4  # Max parts sent to worker but not yet verified

# Timeout configuration
CONNECT_TIMEOUT_SECONDS = 10  # Connection timeout (reduced for faster failover)
SOCK_READ_TIMEOUT_SECONDS = 300  # Socket read timeout (5 minutes)

# Speed monitoring for CDN failover
MIN_SPEED_MBPS = 1.0  # Minimum acceptable speed in megabits per second
SPEED_CHECK_WINDOW_SECONDS = 120  # Speed monitoring window (2 minutes)

# File paths
DEFAULT_API_URL = "https://cdn.runonflux.io/fluxd/api/latest_bootstrap"
DEFAULT_CDN_URL = "https://cdn.runonflux.io"

# CDN failover configuration
DIRECT_CDN_URLS = [
    "https://cdn-1.runonflux.io",
    "https://cdn-2.runonflux.io",
    "https://cdn-3.runonflux.io",
]


@dataclass
class PartNotification:
    """Notification sent from main process to worker when a part is complete."""

    part_id: int  # Part number (0-indexed)
    filepath: str  # Path to the downloaded part file
    expected_sha256: str  # Expected SHA256 checksum
    size: int  # Size in bytes
    already_verified: bool = False  # True if part already verified (resume scenario)


@dataclass
class VerificationResult:
    """Result sent from worker back to main process after SHA256 verification."""

    part_id: int  # Part number (0-indexed)
    verified: bool  # True if SHA256 matched, False otherwise
    actual_sha256: str  # Actual SHA256 computed (for logging)

"""Public library API for flux-downloader."""

import asyncio
import contextlib
import multiprocessing
import typing
from dataclasses import dataclass
from pathlib import Path

from flux_bootstrap.data_structures import DEFAULT_API_URL, DEFAULT_CDN_URL
from flux_bootstrap.main import _download_bootstrap_impl


@dataclass
class ProgressInfo:
    """Progress information for download callbacks.

    Attributes:
        bytes_downloaded: Total bytes downloaded across all parts
        total_bytes: Total expected bytes
        percent: Download percentage (0-100)
        speed_mbps: Current download speed in Mbps
        cdn_server: Current CDN hostname (e.g., "cdn-1.runonflux.io")
        served_by: x-served-by header value (backend ID, e.g., "cdn-1")
        current_part: Current part being downloaded (1-indexed)
        total_parts: Total number of parts
        source: Source type ("cdn")
    """

    bytes_downloaded: int
    total_bytes: int
    percent: float
    speed_mbps: float
    cdn_server: str | None
    served_by: str | None
    current_part: int
    total_parts: int
    source: str


async def download_bootstrap_async(
    destination: str | Path,
    *,
    api_url: str | None = None,
    cdn_url: str | None = None,
    parts_dir: str | Path | None = None,
    progress_callback: typing.Callable[[dict[str, typing.Any]], None] | None = None,
    cancellation_event: asyncio.Event | None = None,
) -> bool:
    """Download and extract Flux bootstrap files (async API).

    This is the primary async API for library use. Downloads blockchain bootstrap
    files from CDN in parts, verifies with SHA256, and extracts to destination.

    Args:
        destination: Directory where bootstrap will be extracted
        api_url: Optional API endpoint
            (default: https://cdn.runonflux.io/fluxd/api/latest_bootstrap)
        cdn_url: Optional CDN base URL (default: https://cdn.runonflux.io)
        parts_dir: Optional directory for part files
            (default: <destination>/bootstrap_parts)
        progress_callback: Optional callback for progress updates.
            Called with dict containing:
            - bytes_downloaded: int
            - total_bytes: int
            - percent: float (0-100)
            - speed_mbps: float
            - cdn_server: str | None
            - served_by: str | None (x-served-by header, backend ID)
            - current_part: int (1-indexed)
            - total_parts: int
            - source: str ("cdn")
        cancellation_event: Optional asyncio.Event to signal cancellation

    Returns:
        True if download and extraction succeeded, False otherwise

    Raises:
        ValueError: If destination is invalid
        RuntimeError: If download or extraction fails critically

    Example:
        >>> async def main():
        ...     def on_progress(progress):
        ...         print(f"Progress: {progress['percent']:.1f}%")
        ...     success = await download_bootstrap_async(
        ...         "/path/to/destination",
        ...         progress_callback=on_progress
        ...     )
        ...     return success
        >>> asyncio.run(main())
    """
    # Validate and normalize destination
    if not destination:
        raise ValueError("destination cannot be empty")

    dest_path = Path(destination).resolve()

    # Set defaults
    if api_url is None:
        api_url = DEFAULT_API_URL

    if cdn_url is None:
        cdn_url = DEFAULT_CDN_URL

    if parts_dir is None:
        parts_dir_path = dest_path / "bootstrap_parts"
    else:
        parts_dir_path = Path(parts_dir).resolve()

    # Create multiprocessing.Event for internal use (workers need it)
    mp_shutdown_event = multiprocessing.Event()

    # If user provided asyncio.Event, monitor it and bridge to multiprocessing.Event
    monitor_task: asyncio.Task | None = None
    if cancellation_event:

        async def monitor_cancellation():
            """Monitor asyncio.Event and forward to multiprocessing.Event."""
            await cancellation_event.wait()
            mp_shutdown_event.set()

        monitor_task = asyncio.create_task(monitor_cancellation())

    try:
        # Call internal implementation with library mode flags
        result = await _download_bootstrap_impl(
            destination=dest_path,
            parts_dir=parts_dir_path,
            api_url=api_url,
            cdn_url=cdn_url,
            shutdown_event=mp_shutdown_event,
            setup_logging_flag=False,  # Library mode: caller controls logging
            set_process_title=False,  # Library mode: don't change process title
            progress_callback=progress_callback,
        )
        return result

    finally:
        # Cancel monitor task if it's still running
        if monitor_task and not monitor_task.done():
            monitor_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await monitor_task


def download_bootstrap(
    destination: str | Path,
    **kwargs,
) -> bool:
    """Download and extract Flux bootstrap files (sync API).

    Synchronous wrapper for download_bootstrap_async(). Uses asyncio.run() to
    execute the async version.

    Args:
        destination: Directory where bootstrap will be extracted
        **kwargs: Additional arguments passed to download_bootstrap_async()

    Returns:
        True if download and extraction succeeded, False otherwise

    Raises:
        ValueError: If destination is invalid
        RuntimeError: If download or extraction fails critically, or if called
            from within an existing event loop

    Example:
        >>> def on_progress(progress):
        ...     print(f"Progress: {progress['percent']:.1f}%")
        >>> success = download_bootstrap(
        ...     "/path/to/destination",
        ...     progress_callback=on_progress
        ... )
    """
    # Check if we're already in an event loop
    try:
        asyncio.get_running_loop()
        raise RuntimeError(
            "download_bootstrap() cannot be called from within an async "
            "context. Use download_bootstrap_async() instead."
        )
    except RuntimeError as e:
        if "no running event loop" not in str(e).lower():
            raise

    # Run async version
    return asyncio.run(download_bootstrap_async(destination, **kwargs))

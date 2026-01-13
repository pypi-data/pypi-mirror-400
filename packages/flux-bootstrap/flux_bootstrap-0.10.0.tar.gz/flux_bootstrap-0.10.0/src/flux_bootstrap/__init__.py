"""flux-bootstrap - Flux blockchain bootstrap downloader.

This library provides an easy way to download and extract Flux blockchain
bootstrap files from CDN with progress tracking, resume support, and automatic
CDN failover.

Example:
    >>> from flux_bootstrap import download_bootstrap_async
    >>> import asyncio
    >>>
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

from flux_bootstrap.api import (
    ProgressInfo,
    download_bootstrap,
    download_bootstrap_async,
)

__all__ = [
    "download_bootstrap",
    "download_bootstrap_async",
    "ProgressInfo",
]

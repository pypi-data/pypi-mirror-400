"""
CDN failover management for flux-downloader.

Provides intelligent CDN failover when the main proxy CDN fails or is too slow.
Uses x-served-by header to identify which backend CDN served the request and
tries alternative backends.
"""

import logging
import re


def extract_backend_from_header(header_value: str) -> str | None:
    """
    Parse x-served-by header to identify backend CDN.

    Examples:
        - "cdn-1.runonflux.io" → "cdn-1"
        - "cache-cdn-2-xyz" → "cdn-2"
        - "cdn-3" → "cdn-3"

    Args:
        header_value: Value of x-served-by or similar header

    Returns:
        Backend identifier ("cdn-1", "cdn-2", "cdn-3"), or None if not found
    """
    if not header_value:
        return None

    match = re.search(r"cdn-([123])", header_value.lower())
    return f"cdn-{match.group(1)}" if match else None


class SlowDownloadError(Exception):
    """
    Raised when download speed is below threshold for too long.

    This exception triggers CDN failover to try an alternative CDN.
    """

    def __init__(self, speed_mbps: float, served_by: str | None):
        """
        Initialize slow download error.

        Args:
            speed_mbps: Actual download speed in megabits per second
            served_by: Backend CDN that served the request (if known)
        """
        self.speed_mbps = speed_mbps
        self.served_by = served_by
        super().__init__(
            f"Download too slow: {speed_mbps:.2f} Mbps (served by: {served_by})"
        )


class CDNFailoverStrategy:
    """
    Manages CDN failover strategy for a single part download.

    Implements 2+1+1+1 attempt strategy:
    - Phase 1 (proxy): 2 attempts on main proxy CDN
    - Phase 2 (direct): 1 attempt each on 3 direct backend CDNs

    Smart ordering: If proxy identified which backend served the request,
    try that backend LAST in direct phase (other backends first).
    """

    def __init__(self, proxy_url: str, direct_urls: list[str]):
        """
        Initialize failover strategy.

        Args:
            proxy_url: Main proxy CDN URL (e.g., https://cdn.runonflux.io)
            direct_urls: List of direct backend CDN URLs
        """
        self.proxy_url = proxy_url
        self.direct_urls = direct_urls.copy()  # Don't mutate original list

        # State tracking
        self.phase = "proxy"  # "proxy" or "direct"
        self.proxy_attempts = 0
        self.direct_index = 0
        self.last_served_by: str | None = None
        self.direct_cdn_order: list[str] = []

        # Attempt limits
        self.max_proxy_attempts = 2
        self.max_direct_attempts = len(direct_urls)  # 1 per backend

    def get_next_cdn(self) -> tuple[str | None, int, int]:
        """
        Get next CDN to try.

        Returns:
            Tuple of (cdn_url, attempt_number, max_attempts_for_this_cdn)
            Returns (None, 0, 0) if all attempts exhausted
        """
        if self.phase == "proxy":
            if self.proxy_attempts < self.max_proxy_attempts:
                self.proxy_attempts += 1
                return (self.proxy_url, self.proxy_attempts, self.max_proxy_attempts)
            else:
                # Transition to direct phase
                self._initialize_direct_phase()
                self.phase = "direct"
                # Fall through to direct phase logic

        if self.phase == "direct" and self.direct_index < len(self.direct_cdn_order):
            cdn_url = self.direct_cdn_order[self.direct_index]
            self.direct_index += 1
            # Each direct CDN gets 1 attempt
            return (cdn_url, 1, 1)

        # All attempts exhausted
        return (None, 0, 0)

    def _initialize_direct_phase(self) -> None:
        """
        Initialize direct CDN phase with smart ordering.

        If last_served_by is known, put that backend LAST in the order.
        Rationale: If proxy via cdn-2 failed, cdn-2 might be blocked for this user.
        """
        if not self.last_served_by:
            # No backend identified, use default order
            self.direct_cdn_order = self.direct_urls.copy()
            return

        # Find the backend URL that matches last_served_by
        identified_backend_url = None
        other_backends = []

        for url in self.direct_urls:
            backend_id = extract_backend_from_header(url)
            if backend_id == self.last_served_by:
                identified_backend_url = url
            else:
                other_backends.append(url)

        # Smart ordering: try other backends first, identified backend last
        if identified_backend_url:
            self.direct_cdn_order = other_backends + [identified_backend_url]
            logging.info(
                f"CDN ordering: Trying {len(other_backends)} other backends "
                f"before {self.last_served_by}"
            )
        else:
            # Backend not found in direct URLs (shouldn't happen)
            self.direct_cdn_order = self.direct_urls.copy()

    def record_failure(
        self, served_by_header: str | None, reason: str
    ) -> None:
        """
        Record a failure for the current CDN attempt.

        Args:
            served_by_header: Value of x-served-by header (if available)
            reason: Human-readable failure reason (for logging)
        """
        # Extract backend identifier from header
        if served_by_header and self.phase == "proxy":
            backend_id = extract_backend_from_header(served_by_header)
            if backend_id:
                self.last_served_by = backend_id
                logging.debug(f"Identified backend from proxy: {backend_id}")

        logging.debug(
            f"CDN failure in {self.phase} phase: {reason} "
            f"(served_by: {served_by_header or 'unknown'})"
        )

    def get_phase_summary(self) -> str:
        """
        Get human-readable summary of current phase.

        Returns:
            Summary string for logging
        """
        if self.phase == "proxy":
            return f"proxy phase ({self.proxy_attempts}/{self.max_proxy_attempts})"
        else:
            return f"direct phase ({self.direct_index}/{len(self.direct_cdn_order)})"


class CDNManager:
    """
    Manages CDN configuration and provides failover strategies.

    Coordinates between main proxy CDN and direct backend CDNs.
    """

    def __init__(
        self,
        proxy_url: str = "https://cdn.runonflux.io",
        direct_urls: list[str] | None = None,
    ):
        """
        Initialize CDN manager.

        Args:
            proxy_url: Main proxy CDN URL
            direct_urls: List of direct backend CDN URLs (defaults to cdn-1/2/3)
        """
        self.proxy_url = proxy_url

        if direct_urls is None:
            # Default to standard Flux CDN backends
            self.direct_urls = [
                "https://cdn-1.runonflux.io",
                "https://cdn-2.runonflux.io",
                "https://cdn-3.runonflux.io",
            ]
        else:
            self.direct_urls = direct_urls

        logging.debug(
            f"CDN Manager initialized: proxy={proxy_url}, "
            f"direct={len(self.direct_urls)} backends"
        )

    def create_failover_strategy(self) -> CDNFailoverStrategy:
        """
        Create a new failover strategy for a part download.

        Each part download gets its own independent strategy instance.

        Returns:
            New CDNFailoverStrategy instance
        """
        return CDNFailoverStrategy(self.proxy_url, self.direct_urls)

    def get_proxy_url(self) -> str:
        """
        Get main proxy CDN URL.

        Returns:
            Proxy CDN URL
        """
        return self.proxy_url

    def get_direct_urls(self) -> list[str]:
        """
        Get list of direct backend CDN URLs.

        Returns:
            List of backend CDN URLs
        """
        return self.direct_urls.copy()

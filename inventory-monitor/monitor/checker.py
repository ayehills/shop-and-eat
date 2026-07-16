"""The Checker owns the HTTP session and enforces polite per-domain pacing."""

from __future__ import annotations

import time
from urllib.parse import urlparse

import requests

from .adapters import build_adapter
from .config import Settings
from .models import CheckResult, WatchTarget


class Checker:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": settings.user_agent,
                "Accept": "text/html,application/json,application/xhtml+xml,*/*",
                "Accept-Language": "en-US,en;q=0.9",
            }
        )
        self._last_hit: dict[str, float] = {}  # domain -> monotonic timestamp

    def _respect_domain_gap(self, url: str) -> None:
        """Never hammer a single domain faster than per_domain_min_gap_seconds."""
        domain = urlparse(url).netloc
        gap = self.settings.per_domain_min_gap_seconds
        now = time.monotonic()
        last = self._last_hit.get(domain)
        if last is not None:
            wait = gap - (now - last)
            if wait > 0:
                time.sleep(wait)
        self._last_hit[domain] = time.monotonic()

    def check(self, target: WatchTarget) -> CheckResult:
        adapter = build_adapter(target, self.session, self.settings.request_timeout)
        last_error = None
        for attempt in range(self.settings.max_retries + 1):
            self._respect_domain_gap(target.url)
            result = adapter.check(target)
            if result.stock.value != "error":
                return result
            last_error = result.error
            if attempt < self.settings.max_retries:
                time.sleep(1.5 * (attempt + 1))  # small linear backoff between retries
        return CheckResult.error_result(last_error or "unknown error")

    def close(self) -> None:
        self.session.close()

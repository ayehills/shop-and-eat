"""Base adapter interface + shared HTTP helper."""

from __future__ import annotations

import abc
from typing import Any

import requests

from ..models import CheckResult, WatchTarget


class Adapter(abc.ABC):
    """An adapter knows how to turn one URL into a CheckResult."""

    def __init__(self, session: requests.Session, timeout: int):
        self.session = session
        self.timeout = timeout

    @abc.abstractmethod
    def check(self, target: WatchTarget) -> CheckResult:
        ...

    # --- shared helpers -------------------------------------------------
    def _get(self, url: str) -> requests.Response:
        resp = self.session.get(url, timeout=self.timeout, allow_redirects=True)
        resp.raise_for_status()
        return resp

    @staticmethod
    def resolve_path(data: Any, dotted: str) -> Any:
        """Walk a dotted path into nested dict/list JSON.

        "product.variants.0.available" -> data["product"]["variants"][0]["available"]
        Raises KeyError/IndexError/TypeError if the path is invalid.
        """
        cur = data
        for part in dotted.split("."):
            if isinstance(cur, list):
                cur = cur[int(part)]
            else:
                cur = cur[part]
        return cur

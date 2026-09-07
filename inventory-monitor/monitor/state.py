"""Persist the last-known stock state so restarts don't re-spam alerts."""

from __future__ import annotations

import json
import os
import tempfile
from typing import Optional


class StateStore:
    def __init__(self, path: str):
        self.path = path
        self._data: dict[str, dict] = {}
        self._load()

    def _load(self) -> None:
        if os.path.exists(self.path):
            try:
                with open(self.path, "r", encoding="utf-8") as fh:
                    self._data = json.load(fh)
            except (json.JSONDecodeError, OSError):
                self._data = {}

    def last_stock(self, key: str) -> Optional[str]:
        entry = self._data.get(key)
        return entry.get("stock") if entry else None

    def update(self, key: str, stock: str, price: Optional[str], detail: Optional[str]) -> None:
        self._data[key] = {"stock": stock, "price": price, "detail": detail}
        self._save()

    def _save(self) -> None:
        # Atomic write so a crash mid-write can't corrupt the state file.
        directory = os.path.dirname(os.path.abspath(self.path)) or "."
        fd, tmp = tempfile.mkstemp(dir=directory, suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as fh:
                json.dump(self._data, fh, indent=2)
            os.replace(tmp, self.path)
        except OSError:
            if os.path.exists(tmp):
                os.remove(tmp)
            raise

"""Load and validate the YAML config into typed objects."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any, Optional

import yaml

from .models import WatchTarget

DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (compatible; inventory-monitor/1.0; personal restock alerts)"
)


@dataclass
class Settings:
    poll_interval_seconds: int = 90
    jitter_seconds: int = 30
    request_timeout: int = 15
    max_retries: int = 2
    user_agent: str = DEFAULT_USER_AGENT
    per_domain_min_gap_seconds: float = 5.0  # never hit one domain faster than this

    # Notifications
    desktop_notifications: bool = True
    sound_alert: bool = True
    console_alert: bool = True
    open_browser_on_restock: bool = False
    discord_webhook: str = ""

    # Quiet hours: list of "HH:MM-HH:MM" strings (local time) during which
    # only console logging happens (no desktop/sound/push).
    quiet_hours: list[str] = field(default_factory=list)

    # Where to persist last-seen stock state so we don't re-alert on restart.
    state_file: str = "monitor_state.json"


@dataclass
class CheckoutProfile:
    """NON-sensitive info to speed up guest checkout via copy-to-clipboard.

    Intentionally has NO fields for card numbers, CVV, or passwords. This is
    the same class of data your browser already stores for address autofill.
    """

    full_name: str = ""
    email: str = ""
    phone: str = ""
    address1: str = ""
    address2: str = ""
    city: str = ""
    state: str = ""
    postal_code: str = ""
    country: str = ""

    def is_populated(self) -> bool:
        return any([self.full_name, self.email, self.address1])

    def as_lines(self) -> str:
        parts = [
            self.full_name,
            self.address1,
            self.address2,
            f"{self.city}, {self.state} {self.postal_code}".strip(", "),
            self.country,
            self.email,
            self.phone,
        ]
        return "\n".join(p for p in parts if p and p.strip())


@dataclass
class Config:
    settings: Settings
    profile: CheckoutProfile
    watch: list[WatchTarget]

    @property
    def enabled_targets(self) -> list[WatchTarget]:
        return [t for t in self.watch if t.enabled]


def _known_fields(cls) -> set[str]:
    return set(getattr(cls, "__dataclass_fields__").keys())


def load_config(path: str) -> Config:
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Config not found: {path}\n"
            "Copy config.example.yaml to config.yaml and edit it."
        )

    with open(path, "r", encoding="utf-8") as fh:
        raw: dict[str, Any] = yaml.safe_load(fh) or {}

    settings = _build(Settings, raw.get("settings", {}) or {})
    profile = _build(CheckoutProfile, raw.get("profile", {}) or {})

    watch_raw = raw.get("watch", []) or []
    targets: list[WatchTarget] = []
    allowed = _known_fields(WatchTarget)
    for i, item in enumerate(watch_raw):
        if not isinstance(item, dict):
            raise ValueError(f"watch[{i}] must be a mapping, got {type(item).__name__}")
        if not item.get("name") or not item.get("url"):
            raise ValueError(f"watch[{i}] requires both 'name' and 'url'")
        filtered = {k: v for k, v in item.items() if k in allowed}
        targets.append(WatchTarget(**filtered))

    if not targets:
        raise ValueError("No watch targets configured. Add at least one under 'watch:'.")

    return Config(settings=settings, profile=profile, watch=targets)


def _build(cls, data: dict[str, Any]):
    allowed = _known_fields(cls)
    unknown = set(data) - allowed
    if unknown:
        # Warn but don't crash — forward-compatibility for new keys.
        print(f"[config] Ignoring unknown keys for {cls.__name__}: {sorted(unknown)}")
    filtered = {k: v for k, v in data.items() if k in allowed}
    return cls(**filtered)

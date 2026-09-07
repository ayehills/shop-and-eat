"""Multi-channel notifications: console, desktop, sound, Discord webhook.

Everything degrades gracefully: a missing optional dependency or a failing
channel logs a warning and never crashes the monitor loop.
"""

from __future__ import annotations

import sys
import webbrowser
from datetime import datetime
from typing import Optional

from rich.console import Console

from .config import Settings

console = Console()


class Notifier:
    def __init__(self, settings: Settings):
        self.settings = settings
        self._desktop_backend = self._init_desktop()

    # --- setup ----------------------------------------------------------
    def _init_desktop(self):
        if not self.settings.desktop_notifications:
            return None
        try:
            from plyer import notification  # type: ignore

            return notification
        except Exception:  # noqa: BLE001
            console.print(
                "[yellow][notify] plyer not available — desktop popups disabled "
                "(pip install plyer). Console/sound alerts still work.[/yellow]"
            )
            return None

    def _in_quiet_hours(self) -> bool:
        if not self.settings.quiet_hours:
            return False
        now = datetime.now().time()
        for window in self.settings.quiet_hours:
            try:
                start_s, end_s = window.split("-")
                start = datetime.strptime(start_s.strip(), "%H:%M").time()
                end = datetime.strptime(end_s.strip(), "%H:%M").time()
            except ValueError:
                continue
            if start <= end:
                if start <= now <= end:
                    return True
            else:  # window wraps past midnight, e.g. 23:00-07:00
                if now >= start or now <= end:
                    return True
        return False

    # --- public API -----------------------------------------------------
    def restock(self, name: str, url: str, price: Optional[str], detail: Optional[str]) -> None:
        price_str = f"  {price}" if price else ""
        headline = f"IN STOCK: {name}{price_str}"
        self._console_banner(headline, url, detail, style="bold green")

        quiet = self._in_quiet_hours()
        if quiet:
            console.print("[dim][notify] quiet hours — console only[/dim]")
            return

        if self.settings.sound_alert:
            self._beep()
        if self._desktop_backend:
            self._desktop(headline, f"{url}")
        if self.settings.discord_webhook:
            self._discord(headline, url, detail)
        if self.settings.open_browser_on_restock:
            try:
                webbrowser.open(url)
            except Exception:  # noqa: BLE001
                pass

    def went_oos(self, name: str) -> None:
        console.print(f"[dim]{_ts()}  sold out again: {name}[/dim]")

    def info(self, message: str) -> None:
        if self.settings.console_alert:
            console.print(f"[dim]{_ts()}  {message}[/dim]")

    def error(self, name: str, message: str) -> None:
        console.print(f"[red]{_ts()}  error checking {name}: {message}[/red]")

    # --- channels -------------------------------------------------------
    def _console_banner(self, headline, url, detail, style):
        console.rule(style=style)
        console.print(f"[{style}]{_ts()}  {headline}[/{style}]")
        console.print(f"    {url}")
        if detail:
            console.print(f"    [dim]{detail}[/dim]")
        console.rule(style=style)

    def _beep(self):
        try:
            sys.stdout.write("\a")
            sys.stdout.flush()
        except Exception:  # noqa: BLE001
            pass

    def _desktop(self, title: str, message: str):
        try:
            self._desktop_backend.notify(
                title=title[:64], message=message[:240],
                app_name="inventory-monitor", timeout=10,
            )
        except Exception as exc:  # noqa: BLE001
            console.print(f"[yellow][notify] desktop popup failed: {exc}[/yellow]")

    def _discord(self, headline: str, url: str, detail: Optional[str]):
        try:
            import requests

            content = f"**{headline}**\n{url}"
            if detail:
                content += f"\n_{detail}_"
            resp = requests.post(
                self.settings.discord_webhook,
                json={"content": content},
                timeout=10,
            )
            if resp.status_code >= 300:
                console.print(
                    f"[yellow][notify] Discord returned {resp.status_code}[/yellow]"
                )
        except Exception as exc:  # noqa: BLE001
            console.print(f"[yellow][notify] Discord webhook failed: {exc}[/yellow]")


def _ts() -> str:
    return datetime.now().strftime("%H:%M:%S")

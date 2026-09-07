"""The polling loop: check every target, diff against last state, alert on change."""

from __future__ import annotations

import random
import time

from rich.console import Console
from rich.table import Table

from .checker import Checker
from .config import Config
from .models import Stock, WatchTarget
from .notifier import Notifier
from .state import StateStore

console = Console()


class Monitor:
    def __init__(self, config: Config):
        self.config = config
        self.checker = Checker(config.settings)
        self.notifier = Notifier(config.settings)
        self.state = StateStore(config.settings.state_file)

    @staticmethod
    def _key(target: WatchTarget) -> str:
        return f"{target.name}::{target.url}"

    def check_once(self, announce_initial: bool = False) -> None:
        """Run one pass over all enabled targets."""
        for target in self.config.enabled_targets:
            key = self._key(target)
            result = self.checker.check(target)

            if result.stock is Stock.ERROR:
                self.notifier.error(target.name, result.error or "unknown")
                continue

            prev = self.state.last_stock(key)
            now = result.stock.value

            if result.stock is Stock.IN_STOCK:
                first_time = prev is None
                changed = prev != now
                if changed or (announce_initial and first_time):
                    self.notifier.restock(target.name, target.url,
                                          result.price, result.detail)
                else:
                    self.notifier.info(f"still in stock: {target.name}")
            elif result.stock is Stock.OUT_OF_STOCK:
                if prev == Stock.IN_STOCK.value:
                    self.notifier.went_oos(target.name)
                else:
                    self.notifier.info(f"out of stock: {target.name}")
            else:  # UNKNOWN
                self.notifier.info(f"unknown state: {target.name} — {result.detail}")

            self.state.update(key, now, result.price, result.detail)

    def run_forever(self) -> None:
        s = self.config.settings
        self._print_startup()
        # First pass announces anything already in stock, so you know your
        # baseline the moment you launch.
        self.check_once(announce_initial=True)
        try:
            while True:
                sleep_for = s.poll_interval_seconds + random.uniform(0, s.jitter_seconds)
                self.notifier.info(f"next check in {sleep_for:.0f}s")
                time.sleep(sleep_for)
                self.check_once(announce_initial=False)
        except KeyboardInterrupt:
            console.print("\n[cyan]Stopped. Bye![/cyan]")
        finally:
            self.checker.close()

    def _print_startup(self):
        s = self.config.settings
        table = Table(title="Watching for restocks", show_edge=False, pad_edge=False)
        table.add_column("#", justify="right", style="dim")
        table.add_column("Name", style="bold")
        table.add_column("URL", style="cyan", overflow="fold")
        for i, t in enumerate(self.config.enabled_targets, 1):
            table.add_row(str(i), t.name, t.url)
        console.print(table)
        console.print(
            f"[dim]Poll ~every {s.poll_interval_seconds}s "
            f"(+0-{s.jitter_seconds}s jitter). "
            f"Desktop={s.desktop_notifications} Sound={s.sound_alert} "
            f"Discord={'on' if s.discord_webhook else 'off'} "
            f"Auto-open={s.open_browser_on_restock}. Ctrl-C to quit.[/dim]\n"
        )

"""Command-line entry point."""

from __future__ import annotations

import argparse
import sys

from rich.console import Console

from . import __version__
from .config import load_config
from .profile import copy_profile, show_profile
from .runner import Monitor

console = Console()


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="inventory-monitor",
        description="Watch trading-card products (ONE PIECE, Pokemon, ...) and "
                    "alert you the moment they restock. Does not auto-purchase.",
    )
    p.add_argument("-c", "--config", default="config.yaml",
                   help="Path to config file (default: config.yaml)")
    p.add_argument("--version", action="version", version=f"%(prog)s {__version__}")

    sub = p.add_subparsers(dest="command")
    sub.add_parser("run", help="Start the monitor loop (default)")
    sub.add_parser("once", help="Check every target a single time, then exit")
    sub.add_parser("list", help="List configured targets and exit")

    prof = sub.add_parser("profile", help="Guest-checkout quick-fill helpers")
    prof.add_argument("action", choices=["show", "copy"],
                      help="show: print your saved shipping/contact block; "
                           "copy: copy it to the clipboard")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    command = args.command or "run"

    try:
        config = load_config(args.config)
    except (FileNotFoundError, ValueError) as exc:
        console.print(f"[red]Config error:[/red] {exc}")
        return 2

    if command == "list":
        for i, t in enumerate(config.enabled_targets, 1):
            console.print(f"{i:>2}. [bold]{t.name}[/bold]  [cyan]{t.url}[/cyan]")
        return 0

    if command == "profile":
        if args.action == "show":
            show_profile(config.profile)
        else:
            copy_profile(config.profile)
        return 0

    monitor = Monitor(config)
    if command == "once":
        monitor.check_once(announce_initial=True)
        monitor.checker.close()
        return 0

    # default: run forever
    monitor.run_forever()
    return 0


if __name__ == "__main__":
    sys.exit(main())

"""Quick-fill checkout profile helper.

This exists to make GUEST checkout faster WITHOUT storing anything sensitive.
It copies your shipping/contact block to the clipboard so you can paste it into
a store's guest-checkout form. Your browser's own autofill handles card entry.

Deliberately unsupported here, by design:
  * no card number / expiry / CVV storage
  * no account username / password storage
  * no automated form submission or purchase
See README.md for why.
"""

from __future__ import annotations

from rich.console import Console
from rich.panel import Panel

from .config import CheckoutProfile

console = Console()


def show_profile(profile: CheckoutProfile) -> None:
    if not profile.is_populated():
        console.print(
            "[yellow]No checkout profile set. Add name/email/address under "
            "'profile:' in config.yaml to enable quick-fill.[/yellow]"
        )
        return
    console.print(Panel(profile.as_lines(), title="Guest checkout quick-fill",
                        subtitle="shipping/contact only — no payment data",
                        expand=False))


def copy_profile(profile: CheckoutProfile) -> bool:
    """Copy the profile block to the clipboard. Returns True on success."""
    if not profile.is_populated():
        console.print("[yellow]Nothing to copy — profile is empty.[/yellow]")
        return False
    try:
        import pyperclip  # type: ignore

        pyperclip.copy(profile.as_lines())
        console.print("[green]Copied guest-checkout details to clipboard.[/green]")
        return True
    except Exception:  # noqa: BLE001
        console.print(
            "[yellow]Clipboard copy needs pyperclip (pip install pyperclip). "
            "Here's the block to copy manually:[/yellow]"
        )
        console.print(profile.as_lines())
        return False

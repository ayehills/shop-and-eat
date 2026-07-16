"""Generic adapters for non-Shopify stores: CSS-selector and JSON-path.

These cover the long tail of retailers. You tell the tool how to read the
page (a selector that appears only when buyable, a "Sold Out" string, a JSON
field, etc.) and it applies that rule on every poll.
"""

from __future__ import annotations

import json as jsonlib

from bs4 import BeautifulSoup

from ..models import CheckResult, Stock, WatchTarget
from .base import Adapter


class CssSelectorAdapter(Adapter):
    """Decide stock from the rendered HTML using a rule in the target config.

    in_stock_when:
      selector_present  -> IN_STOCK when `selector` matches at least one node
      selector_absent   -> IN_STOCK when `selector` matches nothing
      text_contains     -> IN_STOCK when page text contains `match_text`
      text_absent       -> IN_STOCK when page text does NOT contain `match_text`
    """

    def check(self, target: WatchTarget) -> CheckResult:
        try:
            resp = self._get(target.url)
            soup = BeautifulSoup(resp.text, "html.parser")
        except Exception as exc:  # noqa: BLE001
            return CheckResult.error_result(f"{type(exc).__name__}: {exc}")

        title = soup.title.get_text(strip=True) if soup.title else None
        price = None
        if target.price_selector:
            node = soup.select_one(target.price_selector)
            if node:
                price = node.get_text(strip=True)

        mode = target.in_stock_when
        try:
            if mode in ("selector_present", "selector_absent"):
                if not target.selector:
                    return CheckResult.error_result(
                        f"'{mode}' requires a 'selector' in config")
                found = soup.select(target.selector)
                present = len(found) > 0
                in_stock = present if mode == "selector_present" else not present
                detail = f"selector {'matched' if present else 'no match'}: {target.selector}"

            elif mode in ("text_contains", "text_absent"):
                if not target.match_text:
                    return CheckResult.error_result(
                        f"'{mode}' requires 'match_text' in config")
                haystack = soup.get_text(" ", strip=True).lower()
                contains = target.match_text.lower() in haystack
                in_stock = contains if mode == "text_contains" else not contains
                detail = f"text {'contains' if contains else 'missing'}: {target.match_text!r}"

            else:
                return CheckResult.error_result(f"Unknown in_stock_when: {mode!r}")
        except Exception as exc:  # noqa: BLE001
            return CheckResult.error_result(f"parse error: {type(exc).__name__}: {exc}")

        return CheckResult(
            stock=Stock.IN_STOCK if in_stock else Stock.OUT_OF_STOCK,
            title=title,
            price=price,
            detail=detail,
        )


class JsonPathAdapter(Adapter):
    """Decide stock from a JSON API using a dotted `availability_path`."""

    def check(self, target: WatchTarget) -> CheckResult:
        if not target.availability_path:
            return CheckResult.error_result(
                "json target requires 'availability_path'")
        try:
            resp = self._get(target.url)
            data = resp.json()
        except jsonlib.JSONDecodeError as exc:
            return CheckResult.error_result(f"response was not JSON: {exc}")
        except Exception as exc:  # noqa: BLE001
            return CheckResult.error_result(f"{type(exc).__name__}: {exc}")

        try:
            value = self.resolve_path(data, target.availability_path)
        except (KeyError, IndexError, TypeError, ValueError) as exc:
            return CheckResult(
                Stock.UNKNOWN,
                detail=f"availability_path not found: {target.availability_path} ({exc})",
            )

        in_stock = self._interpret(value, target.in_stock_values)

        price = None
        if target.price_path:
            try:
                price = str(self.resolve_path(data, target.price_path))
            except (KeyError, IndexError, TypeError, ValueError):
                price = None

        return CheckResult(
            stock=Stock.IN_STOCK if in_stock else Stock.OUT_OF_STOCK,
            price=price,
            detail=f"{target.availability_path} = {value!r}",
        )

    @staticmethod
    def _interpret(value, in_stock_values: list[str]) -> bool:
        if isinstance(value, bool):
            return value
        if isinstance(value, (int, float)):
            return value > 0
        if isinstance(value, str):
            return value.strip().lower() in {v.lower() for v in in_stock_values}
        if isinstance(value, (list, dict)):
            return len(value) > 0
        return False

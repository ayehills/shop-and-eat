"""Core data types shared across the monitor."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class Stock(str, Enum):
    """Result of a single stock check."""

    IN_STOCK = "in_stock"
    OUT_OF_STOCK = "out_of_stock"
    UNKNOWN = "unknown"  # page fetched but availability could not be determined
    ERROR = "error"      # fetch or parse failed

    @property
    def is_buyable(self) -> bool:
        return self is Stock.IN_STOCK


@dataclass
class CheckResult:
    """Everything we learned from checking one watch target once."""

    stock: Stock
    price: Optional[str] = None
    title: Optional[str] = None
    detail: Optional[str] = None          # human-readable note (e.g. matched selector)
    error: Optional[str] = None           # populated when stock is ERROR
    raw_available_count: Optional[int] = None  # e.g. number of in-stock Shopify variants

    @classmethod
    def error_result(cls, message: str) -> "CheckResult":
        return cls(stock=Stock.ERROR, error=message)


@dataclass
class WatchTarget:
    """A single product the user wants to monitor."""

    name: str
    url: str
    type: str = "auto"  # auto | shopify | shopify_collection | json | css

    # --- css adapter options ---
    # How to interpret the page. One of:
    #   selector_present  -> in stock when `selector` matches an element
    #   selector_absent   -> in stock when `selector` matches nothing
    #   text_contains     -> in stock when page text contains `match_text`
    #   text_absent       -> in stock when page text does NOT contain `match_text`
    in_stock_when: str = "selector_present"
    selector: Optional[str] = None
    match_text: Optional[str] = None
    price_selector: Optional[str] = None

    # --- json adapter options ---
    # Dotted path into the JSON response, e.g. "product.available" or
    # "data.0.inStock". Array indices are written as plain integers.
    availability_path: Optional[str] = None
    # If availability_path resolves to a string, treat these (lowercased) as
    # "in stock". If it resolves to a bool/number, truthiness is used.
    in_stock_values: list[str] = field(default_factory=lambda: ["true", "instock", "in_stock", "available", "1"])
    price_path: Optional[str] = None

    # Optional per-target overrides
    enabled: bool = True
    notes: Optional[str] = None

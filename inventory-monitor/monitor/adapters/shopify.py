"""Adapters for Shopify-backed stores.

A large share of TCG / hobby retailers run on Shopify, which exposes public,
read-only JSON for products. We use those endpoints instead of scraping
rendered HTML — they're stable, lightweight, and give exact per-variant
availability.

  * Product page:  https://store.com/products/<handle>
      -> append ".json"  =>  {"product": {"variants": [{"available": bool, ...}]}}
  * Collection:    https://store.com/collections/<handle>
      -> append "/products.json" => {"products": [ ... ]}
"""

from __future__ import annotations

import re

from ..models import CheckResult, Stock, WatchTarget
from .base import Adapter

_PRODUCT_URL = re.compile(r"/products/[^/?#]+")
_COLLECTION_URL = re.compile(r"/collections/[^/?#]+")


def looks_like_shopify_product(url: str) -> bool:
    return bool(_PRODUCT_URL.search(url))


def looks_like_shopify_collection(url: str) -> bool:
    return bool(_COLLECTION_URL.search(url)) and "/products/" not in url


def _strip_query(url: str) -> str:
    return re.split(r"[?#]", url, 1)[0].rstrip("/")


def _fmt_price(variant: dict) -> str | None:
    price = variant.get("price")
    if price is None:
        return None
    return f"${price}"


class ShopifyProductAdapter(Adapter):
    def check(self, target: WatchTarget) -> CheckResult:
        json_url = _strip_query(target.url) + ".json"
        try:
            resp = self._get(json_url)
            data = resp.json()
        except Exception as exc:  # noqa: BLE001 - report any fetch/parse failure
            return CheckResult.error_result(f"{type(exc).__name__}: {exc}")

        product = data.get("product") or {}
        variants = product.get("variants") or []
        title = product.get("title")

        available = [v for v in variants if v.get("available")]
        if not variants:
            return CheckResult(Stock.UNKNOWN, title=title,
                               detail="No variants in product JSON")

        if available:
            cheapest = min(available, key=lambda v: float(v.get("price") or 1e12))
            return CheckResult(
                stock=Stock.IN_STOCK,
                title=title,
                price=_fmt_price(cheapest),
                raw_available_count=len(available),
                detail=f"{len(available)}/{len(variants)} variant(s) available",
            )
        return CheckResult(Stock.OUT_OF_STOCK, title=title,
                           detail=f"0/{len(variants)} variant(s) available")


class ShopifyCollectionAdapter(Adapter):
    """Watch a whole collection; in stock if ANY product has an available variant."""

    def check(self, target: WatchTarget) -> CheckResult:
        json_url = _strip_query(target.url) + "/products.json?limit=250"
        try:
            resp = self._get(json_url)
            data = resp.json()
        except Exception as exc:  # noqa: BLE001
            return CheckResult.error_result(f"{type(exc).__name__}: {exc}")

        products = data.get("products") or []
        if not products:
            return CheckResult(Stock.UNKNOWN, detail="Empty collection JSON")

        in_stock_titles: list[str] = []
        for p in products:
            if any(v.get("available") for v in (p.get("variants") or [])):
                in_stock_titles.append(p.get("title", "?"))

        if in_stock_titles:
            preview = "; ".join(in_stock_titles[:3])
            more = f" (+{len(in_stock_titles) - 3} more)" if len(in_stock_titles) > 3 else ""
            return CheckResult(
                stock=Stock.IN_STOCK,
                raw_available_count=len(in_stock_titles),
                detail=f"In stock: {preview}{more}",
            )
        return CheckResult(Stock.OUT_OF_STOCK,
                           detail=f"0/{len(products)} products available")

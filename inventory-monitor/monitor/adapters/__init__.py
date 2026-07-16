"""Adapter registry + auto-detection."""

from __future__ import annotations

import requests

from ..models import WatchTarget
from .base import Adapter
from .generic import CssSelectorAdapter, JsonPathAdapter
from .shopify import (
    ShopifyCollectionAdapter,
    ShopifyProductAdapter,
    looks_like_shopify_collection,
    looks_like_shopify_product,
)


def resolve_adapter_type(target: WatchTarget) -> str:
    """Return a concrete adapter type, resolving 'auto'."""
    if target.type != "auto":
        return target.type
    if looks_like_shopify_collection(target.url):
        return "shopify_collection"
    if looks_like_shopify_product(target.url):
        return "shopify"
    if target.availability_path:
        return "json"
    # Fall back to CSS scraping; requires selector/match_text to be set.
    return "css"


def build_adapter(target: WatchTarget, session: requests.Session, timeout: int) -> Adapter:
    kind = resolve_adapter_type(target)
    if kind == "shopify":
        return ShopifyProductAdapter(session, timeout)
    if kind == "shopify_collection":
        return ShopifyCollectionAdapter(session, timeout)
    if kind == "json":
        return JsonPathAdapter(session, timeout)
    if kind == "css":
        return CssSelectorAdapter(session, timeout)
    raise ValueError(f"Unknown adapter type: {kind!r} for target {target.name!r}")


__all__ = ["Adapter", "resolve_adapter_type", "build_adapter"]

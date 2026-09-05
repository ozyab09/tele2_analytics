"""Parsing of Tele2 API payloads into typed data points."""

from __future__ import annotations

from typing import Any

from .metrics import LotDataPoint


def parse_history(data: list[dict[str, Any]]) -> list[LotDataPoint]:
    """Convert API ``data`` records into a list of typed data points.

    Records may be either ``volume`` + ``count`` (as before) or the newer
    ``history``/``cost`` shaped payloads. Unknown kinds are skipped.
    """
    points: list[LotDataPoint] = []
    for item in data:
        if not isinstance(item, dict):
            continue
        try:
            volume = int(item.get("volume", 0))
        except (TypeError, ValueError):
            continue

        count = _coerce(item, ("count",))
        avg_cost = _coerce(item, ("avgCost", "cost"))
        if count is None and avg_cost is None:
            continue

        points.append(LotDataPoint(volume=volume, count=count or 0, avg_cost=avg_cost or 0))
    return points


def _coerce(item: dict[str, Any], keys: tuple[str, ...]) -> int | float | None:
    for key in keys:
        value = item.get(key)
        if value is None:
            continue
        try:
            return int(value)
        except (TypeError, ValueError):
            try:
                return float(value)
            except (TypeError, ValueError):
                continue
    return None

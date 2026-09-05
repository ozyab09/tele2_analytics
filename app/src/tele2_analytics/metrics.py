"""Prometheus metrics for Tele2 lot data."""

from __future__ import annotations

from dataclasses import dataclass

from prometheus_client import Gauge

# Historical cost metric guide: each data point carries a numeric cost per
# volume bucket. We keep a single gauge exposing both count and avg cost.
_lots = Gauge(
    "tele2_lots",
    "Count of lots for sale",
    labelnames=("volume", "metric", "data_type"),
)
_requests = Gauge(
    "tele2_scrape_requests_total",
    "Total number of API requests performed",
    labelnames=("data_type", "result"),
)


@dataclass(frozen=True)
class LotDataPoint:
    """A single lot data point parsed from the API payload."""

    volume: int
    count: int | float = 0
    avg_cost: int | float = 0


def initialise() -> None:
    """Create/reset all registry metrics (idempotent)."""
    _lots._metrics.clear()  # noqa: SLF001 - allow resetting for tests
    _requests._metrics.clear()  # noqa: SLF001


def update(data_type: str, points: list[LotDataPoint]) -> None:
    """Update the lot gauges from parsed data points."""
    for point in points:
        _lots.labels(
            volume=str(point.volume), metric="count", data_type=data_type
        ).set(point.count)
        _lots.labels(
            volume=str(point.volume), metric="avg_cost", data_type=data_type
        ).set(point.avg_cost)


def record_request(data_type: str, ok: bool) -> None:
    _requests.labels(data_type=data_type, result="ok" if ok else "error").inc()

"""Core collection loop orchestration."""

from __future__ import annotations

import logging
import time

from .client import RequestError, Tele2Client
from .config import Settings
from .parser import parse_history

logger = logging.getLogger(__name__)


class Collector:
    """Periodically fetches Tele2 data and updates Prometheus metrics."""

    def __init__(self, settings: Settings, client: Tele2Client) -> None:
        self._settings = settings
        self._client = client

    def collect_once(self) -> dict[str, int]:
        """Fetch and publish metrics for all traffic types.

        Returns a summary mapping traffic type -> number of points published.
        """
        result: dict[str, int] = {}
        for traffic_type in self._settings.traffic_types:
            count = self._collect_traffic_type(traffic_type)
            result[traffic_type] = count
        return result

    def _collect_traffic_type(self, traffic_type: str) -> int:
        try:
            data = self._client.fetch_history(traffic_type)
        except RequestError as exc:
            logger.warning("Skipping '%s': %s", traffic_type, exc)
            return 0

        from . import metrics

        points = parse_history(data)
        metrics.update(traffic_type, points)
        metrics.record_request(traffic_type, ok=True)
        logger.info("Updated %d points for traffic type '%s'", len(points), traffic_type)
        return len(points)

    def run_forever(self) -> None:
        """Run the collection loop until interrupted."""
        logger.info(
            "Starting collection every %d s for types %s",
            self._settings.check_interval,
            ", ".join(self._settings.traffic_types),
        )
        while True:
            try:
                self.collect_once()
            except Exception:  # pragma: no cover - defensive loop guard
                logger.exception("Unexpected error during collection cycle")
            time.sleep(self._settings.check_interval)

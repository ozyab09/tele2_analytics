"""Console entry point for the Tele2 analytics collector."""

from __future__ import annotations

import logging

from prometheus_client import start_http_server

from .client import Tele2Client
from .collector import Collector
from .config import Settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def main() -> None:
    settings = Settings()
    start_http_server(settings.prometheus_port)
    logger.info("Prometheus metrics listening on :%d", settings.prometheus_port)

    client = Tele2Client(settings)
    collector = Collector(settings, client)
    try:
        collector.run_forever()
    finally:
        client.close()


if __name__ == "__main__":
    main()

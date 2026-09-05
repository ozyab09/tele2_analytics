"""HTTP client for the Tele2 Market lots API."""

from __future__ import annotations

import logging
from typing import Any

import requests

from .config import Settings

logger = logging.getLogger(__name__)


class Tele2Client:
    """Thin wrapper around the Tele2 lots API."""

    def __init__(self, settings: Settings, session: requests.Session | None = None) -> None:
        self._settings = settings
        self._session = session or requests.Session()
        self._session.headers.update({"User-Agent": settings.user_agent})

    def fetch_history(self, traffic_type: str) -> list[dict[str, Any]]:
        """Return the raw ``data`` payload for a traffic type.

        Raises:
            RequestError: on network/HTTP errors or unexpected payload shape.
        """
        url = f"{self._settings.api_base_url}?trafficType={traffic_type}"
        try:
            response = self._session.get(url, timeout=self._settings.request_timeout)
            response.raise_for_status()
        except requests.RequestException as exc:
            raise RequestError(f"GET {url} failed: {exc}") from exc

        try:
            payload = response.json()
        except ValueError as exc:
            raise RequestError(f"Invalid JSON from {url}") from exc

        data = payload.get("data")
        if not isinstance(data, list):
            raise RequestError(
                f"Unexpected payload from {url}: expected 'data' list, got {type(data).__name__}"
            )
        return data

    def close(self) -> None:
        self._session.close()


class RequestError(Exception):
    """Raised when fetching or parsing API data fails."""

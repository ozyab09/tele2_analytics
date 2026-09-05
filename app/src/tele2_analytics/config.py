"""Application configuration loaded from environment variables."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from enum import StrEnum


class TrafficType(StrEnum):
    DATA = "data"
    SMS = "sms"
    VOICE = "voice"


@dataclass(frozen=True)
class Settings:
    """Runtime settings, all overridable via environment variables."""

    api_base_url: str = field(
        default_factory=lambda: os.getenv(
            "TELE2_API_URL",
            "https://msk.t2.ru/api/exchange/lots/stats/costs/history",
        )
    )
    traffic_types: tuple[str, ...] = field(
        default_factory=lambda: tuple(
            os.getenv("TELE2_TRAFFIC_TYPES", "data,sms,voice").split(",")
        )
    )
    check_interval: int = field(
        default_factory=lambda: int(os.getenv("CHECK_INTERVAL", "60"))
    )
    prometheus_port: int = field(
        default_factory=lambda: int(os.getenv("PROMETHEUS_PORT", "8080"))
    )
    request_timeout: int = field(
        default_factory=lambda: int(os.getenv("REQUEST_TIMEOUT", "10"))
    )
    user_agent: str = field(
        default_factory=lambda: os.getenv(
            "USER_AGENT",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0 Safari/537.36",
        )
    )

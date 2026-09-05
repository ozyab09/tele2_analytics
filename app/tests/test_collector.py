from tele2_analytics import metrics
from tele2_analytics.collector import Collector
from tele2_analytics.config import Settings
from tele2_analytics.metrics import LotDataPoint
from tele2_analytics.parser import parse_history


class FakeClient:
    def __init__(self, payloads):
        self.payloads = payloads
        self.failures = set()

    def fetch_history(self, traffic_type):
        if traffic_type in self.failures:
            from tele2_analytics.client import RequestError

            raise RequestError("boom")
        return self.payloads.get(traffic_type, [])


def make_collector(payloads=None, traffic_types=("data", "sms", "voice")):
    settings = Settings()
    # replace frozen defaults via object.__setattr__ for tests
    object.__setattr__(settings, "traffic_types", traffic_types)
    return Collector(settings, FakeClient(payloads or {}))


def test_parse_history_skips_non_dicts():
    assert parse_history([None, "x", 1]) == []


def test_parse_history_handles_count_and_avg_cost():
    points = parse_history([{"volume": "20", "count": 5, "avgCost": "3.5"}])
    assert points == [LotDataPoint(volume=20, count=5, avg_cost=3.5)]


def test_parse_history_handles_cost_key():
    points = parse_history([{"volume": 10, "cost": 7}])
    assert points == [LotDataPoint(volume=10, count=0, avg_cost=7)]


def test_parse_history_skips_unparseable_volume():
    assert parse_history([{"volume": "n/a", "count": 1}]) == []


def test_parse_history_skips_empty_records():
    assert parse_history([{"volume": 1}]) == []


def test_collect_once_updates_metrics():
    metrics.initialise()
    collector = make_collector(
        {"data": [{"volume": 10, "count": 4, "avgCost": 2.5}]},
    )
    result = collector.collect_once()
    assert result["data"] == 1
    gauge = metrics._lots.labels(volume="10", metric="count", data_type="data")
    assert gauge._value.get() == 4


def test_collect_once_skips_failing_traffic_type():
    metrics.initialise()
    collector = make_collector(traffic_types=("data",))
    collector._client.failures.add("data")
    result = collector.collect_once()
    assert result["data"] == 0

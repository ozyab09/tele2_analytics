import pytest
import requests
import requests_mock

from tele2_analytics.client import RequestError, Tele2Client
from tele2_analytics.config import Settings


def make_client() -> Tele2Client:
    return Tele2Client(Settings())


def test_fetch_history_returns_data_list():
    with requests_mock.Mocker() as m:
        m.get(requests_mock.ANY, json={"data": [{"volume": 10, "count": 4}]})
        client = make_client()
        data = client.fetch_history("data")
        assert data == [{"volume": 10, "count": 4}]


def test_fetch_history_builds_url_with_traffic_type():
    with requests_mock.Mocker() as m:
        mock = m.get(
            "https://msk.t2.ru/api/exchange/lots/stats/costs/history?trafficType=data",
            json={"data": []},
        )
        client = make_client()
        client.fetch_history("data")
        assert mock.called_once


def test_fetch_history_raises_on_http_error():
    with requests_mock.Mocker() as m:
        m.get(requests_mock.ANY, status_code=500)
        client = make_client()
        with pytest.raises(RequestError):
            client.fetch_history("data")


def test_fetch_history_raises_on_network_error():
    with requests_mock.Mocker() as m:
        m.get(requests_mock.ANY, exc=requests.ConnectionError("boom"))
        client = make_client()
        with pytest.raises(RequestError):
            client.fetch_history("data")


def test_fetch_history_raises_on_invalid_json():
    with requests_mock.Mocker() as m:
        m.get(requests_mock.ANY, text="not json")
        client = make_client()
        with pytest.raises(RequestError):
            client.fetch_history("data")


def test_fetch_history_raises_on_non_list_data():
    with requests_mock.Mocker() as m:
        m.get(requests_mock.ANY, json={"data": {"foo": "bar"}})
        client = make_client()
        with pytest.raises(RequestError):
            client.fetch_history("data")


def test_fetch_history_sets_user_agent():
    with requests_mock.Mocker() as m:
        m.get(requests_mock.ANY, json={"data": []})
        client = make_client()
        client.fetch_history("data")
        req = m.request_history[0]
        assert req.headers["User-Agent"] == Settings().user_agent

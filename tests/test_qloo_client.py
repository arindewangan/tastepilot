"""Tests for qloo_client.py — all HTTP mocked, zero network."""
import pytest
import requests

from qloo_client import (
    ALLOWED_FILTER_TYPES,
    HACKATHON_BASE_URL,
    QlooAPIError,
    QlooClient,
)


class FakeResponse:
    def __init__(self, json_data=None, status_code=200, ok=True):
        self._json = json_data or {}
        self.status_code = status_code
        self.ok = ok

    def json(self):
        return self._json


SAMPLE_INSIGHTS = {
    "success": True,
    "entities": [
        {
            "name": "Britannia & Co.",
            "entity_id": "abc123",
            "affinity": 0.87,
            "popularity": 0.92,
            "tags": [{"name": "heritage"}, "comfort food"],
            "location": {"city": "Mumbai"},
        }
    ],
}


def test_base_url_is_hackathon_only():
    assert HACKATHON_BASE_URL == "https://hackathon.api.qloo.com"


def test_demo_mode_without_key():
    assert QlooClient(api_key=None).demo_mode is True
    assert QlooClient(api_key="").demo_mode is True


def test_live_mode_with_key():
    assert QlooClient(api_key="k").demo_mode is False


def test_search_demo_is_flagged():
    results = QlooClient().search("wes anderson")
    assert results, "demo search should match the catalog"
    assert results[0]["name"] == "Wes Anderson"
    assert results[0]["demo"] is True


def test_insights_demo_places_flagged():
    items = QlooClient().insights("urn:entity:place", take=3)
    assert len(items) == 3
    assert all(i["demo"] is True for i in items)
    assert items[0]["affinity"] == 0.91


def test_insights_invalid_filter_type_raises():
    with pytest.raises(ValueError):
        QlooClient().insights("urn:entity:food_and_drink")


def test_all_documented_types_allowed():
    assert "urn:entity:artist" in ALLOWED_FILTER_TYPES
    assert "urn:entity:place" in ALLOWED_FILTER_TYPES
    assert "urn:entity:movie" in ALLOWED_FILTER_TYPES


def test_insights_live_sends_correct_request(monkeypatch):
    captured = {}

    def fake_get(url, headers=None, params=None, timeout=None):
        captured.update(url=url, headers=headers, params=params)
        return FakeResponse(SAMPLE_INSIGHTS)

    monkeypatch.setattr(requests, "get", fake_get)
    client = QlooClient(api_key="secret-key")
    entities = client.insights(
        "urn:entity:place",
        signal_entities=["id1", "id2"],
        location="Mumbai",
        take=10,
    )
    assert captured["url"] == "https://hackathon.api.qloo.com/v2/insights"
    assert captured["headers"]["X-Api-Key"] == "secret-key"
    assert "Authorization" not in captured["headers"]
    assert captured["params"]["filter.type"] == "urn:entity:place"
    assert captured["params"]["signal.interests.entities"] == "id1,id2"
    assert captured["params"]["filter.location.query"] == "Mumbai"
    e = entities[0]
    assert e["name"] == "Britannia & Co."
    assert e["affinity"] == 0.87
    assert e["tags"] == ["heritage", "comfort food"]
    assert e["demo"] is False


def test_rate_limit_is_retried(monkeypatch):
    calls = []

    def fake_get(url, headers=None, params=None, timeout=None):
        calls.append(1)
        if len(calls) < 3:
            return FakeResponse(status_code=429, ok=False)
        return FakeResponse(SAMPLE_INSIGHTS)

    monkeypatch.setattr(requests, "get", fake_get)
    client = QlooClient(api_key="k").insights("urn:entity:movie")
    assert len(calls) == 3
    assert entities[0]["name"] == "Britannia & Co."


def test_unauthorized_raises_helpful_error(monkeypatch):
    monkeypatch.setattr(
        requests, "get", lambda *a, **k: FakeResponse(status_code=401, ok=False)
    )
    with pytest.raises(QlooAPIError, match="hackathon.api.qloo.com"):
        QlooClient(api_key="bad").insights("urn:entity:place")


def test_search_results_are_cached(monkeypatch):
    calls = []

    def fake_get(url, headers=None, params=None, timeout=None):
        calls.append(1)
        return FakeResponse({"success": True, "results": []})

    monkeypatch.setattr(requests, "get", fake_get)
    client = QlooClient(api_key="k")
    client.search("ramen")
    client.search("ramen")
    assert len(calls) == 1


def test_empty_entities_returned_as_list(monkeypatch):
    monkeypatch.setattr(
        requests, "get", lambda *a, **k: FakeResponse({"success": True, "entities": []})
    )
    assert QlooClient(api_key="k").insights("urn:entity:place") == []

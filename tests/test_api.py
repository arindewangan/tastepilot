"""Tests for app.py routes — Flask test client, zero network (Demo Mode)."""
import pytest

from app import build_app


@pytest.fixture()
def client(monkeypatch):
    monkeypatch.delenv("QLOO_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    return build_app().test_client()


def test_health_reports_demo_mode(client):
    r = client.get("/api/health")
    assert r.status_code == 200
    body = r.get_json()
    assert body["status"] == "ok"
    assert body["demo_mode"] is True
    assert body["has_qloo_key"] is False
    assert "hackathon.api.qloo.com" in body["qloo_base"]


def test_index_serves_html(client):
    r = client.get("/")
    assert r.status_code == 200
    assert b"TastePilot" in r.data


def test_taste_profile_rejects_empty_favorites(client):
    r = client.post("/api/taste-profile", json={"favorites": []})
    assert r.status_code == 400
    r = client.post("/api/taste-profile", json={})
    assert r.status_code == 400


def test_taste_profile_demo(client):
    r = client.post("/api/taste-profile", json={"favorites": ["Wes Anderson", "jazz"]})
    assert r.status_code == 200
    profile = r.get_json()["profile"]
    assert len(profile["entities"]) == 2
    assert profile["demo"] is True
    assert profile["tags"]


def test_plan_rejects_missing_request(client):
    r = client.post("/api/plan", json={"favorites": ["jazz"]})
    assert r.status_code == 400


def test_plan_demo_end_to_end(client):
    r = client.post(
        "/api/plan",
        json={"request": "Plan my Saturday in Mumbai", "favorites": ["jazz", "ramen"]},
    )
    assert r.status_code == 200
    body = r.get_json()
    assert body["intent"]["location"] == "Mumbai"
    assert body["items"], "demo plan must return itinerary items"
    assert all("why" in i and i["why"] for i in body["items"])
    assert body["demo"] is True
    assert any(s["step"] == "insights" for s in body["trace"])


def test_compare_demo(client):
    r = client.post(
        "/api/compare",
        json={"request": "Plan my Saturday in Mumbai", "favorites": ["jazz"]},
    )
    assert r.status_code == 200
    body = r.get_json()
    assert body["qloo"] and body["generic"]

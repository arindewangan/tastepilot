"""Tests for llm.py — HTTP mocked, zero network."""
import requests

from llm import GENERATE_URL, GeminiClient


class FakeResponse:
    def __init__(self, json_data, status_code=200, ok=True):
        self._json = json_data
        self.status_code = status_code
        self.ok = ok

    def json(self):
        return self._json


def gemini_payload(text):
    return {"candidates": [{"content": {"parts": [{"text": text}]}}]}


def test_demo_mode_without_key():
    client = GeminiClient()
    assert client.demo_mode is True
    out = client.generate("taste dna profile summary")
    assert out["demo"] is True
    assert "Demo Mode" in out["text"]


def test_live_generate_parses_text(monkeypatch):
    captured = {}

    def fake_post(url, params=None, json=None, timeout=None):
        captured.update(url=url, params=params, body=json)
        return FakeResponse(gemini_payload("Warm one-liner."))

    monkeypatch.setattr(requests, "post", fake_post)
    out = GeminiClient(api_key="gkey").generate("hello", system="sys")
    assert captured["url"] == GENERATE_URL
    assert captured["params"] == {"key": "gkey"}
    assert out == {"text": "Warm one-liner.", "demo": False}


def test_live_failure_falls_back_to_labeled_demo(monkeypatch):
    def boom(*a, **k):
        raise requests.ConnectionError("offline")

    monkeypatch.setattr(requests, "post", boom)
    out = GeminiClient(api_key="gkey").generate("taste dna profile summary")
    assert out["demo"] is True
    assert "Demo Mode" in out["text"]


def test_explain_pick_demo_is_labeled():
    out = GeminiClient().explain_pick(
        {"name": "Britannia & Co.", "affinity": 0.91, "tags": ["heritage"]},
        ["Wes Anderson"],
    )
    assert out.startswith("[Demo Mode")
    assert "Britannia & Co." in out and "91%" in out


def test_generic_recommendations_demo_flagged():
    items = GeminiClient().generic_recommendations("Plan my Saturday in Mumbai")
    assert len(items) == 4
    assert all(i["demo"] is True for i in items)
    assert items[0]["name"] == "Gateway of India"

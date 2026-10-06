"""Tests for agent.py — Qloo/LLM collaborators are fakes, zero network."""
from agent import TastePilotAgent
from demo_data import demo_insights, demo_search, demo_tags


class FakeQloo:
    def __init__(self, demo=True):
        self._demo = demo

    @property
    def demo_mode(self):
        return self._demo

    def search(self, query):
        return demo_search(query)

    def tags(self, query):
        return demo_tags(query)

    def insights(self, filter_type, **kwargs):
        return demo_insights(filter_type, take=kwargs.get("take", 10))


class FakeLLM:
    def generate(self, prompt, system=None):
        return {"text": "canned narration", "demo": True}

    def explain_pick(self, item, seed_names, demo_profile=False):
        return "why: " + item["name"]

    def generic_recommendations(self, request_text):
        return [{"name": "Generic Spot", "why": "popular", "demo": True}]


def make_agent(demo=True):
    return TastePilotAgent(FakeQloo(demo=demo), FakeLLM())


def test_classify_plan_with_location():
    intent = make_agent().classify_intent("Plan my Saturday in Mumbai")
    assert intent["kind"] == "plan"
    assert intent["location"] == "Mumbai"


def test_classify_budget_parsed():
    intent = make_agent().classify_intent("date night in Bengaluru under ₹2000")
    assert intent["location"] == "Bengaluru"
    assert intent["budget"] == "2000"


def test_build_taste_profile_resolves_and_aggregates():
    result = make_agent().build_taste_profile(["Wes Anderson", "jazz", "ramen"])
    profile = result["profile"]
    assert len(profile["entities"]) == 3
    assert profile["entities"][0]["name"] == "Wes Anderson"
    assert "quirky" in profile["tag_weights"]
    assert profile["summary"] == "canned narration"
    assert profile["demo"] is True
    assert any(s["step"] == "search" for s in result["trace"])


def test_build_profile_skips_unmatched_favorites():
    result = make_agent().build_taste_profile(["zzz-no-such-thing-zzz"])
    assert result["profile"]["entities"] == []
    assert result["profile"]["seed_ids"] == []


def test_plan_returns_affinity_items_with_trace():
    result = make_agent().plan("Plan my Saturday in Mumbai", ["Wes Anderson", "jazz"])
    assert result["intent"]["location"] == "Mumbai"
    assert result["items"], "plan must produce itinerary items"
    places = [i for i in result["items"] if i["kind"] == "place"]
    movies = [i for i in result["items"] if i["kind"] == "movie"]
    assert places and movies, "plan should have both cross-domain legs"
    first = places[0]
    assert first["affinity"] == 0.91
    assert first["why"].startswith("why:")
    assert first["demo"] is True
    steps = [s["step"] for s in result["trace"]]
    assert "classify" in steps and "insights" in steps


def test_plan_default_location_is_mumbai():
    result = make_agent().plan("Plan something fun", ["jazz"])
    assert result["intent"]["location"] == "Mumbai"


def test_compare_returns_both_sides():
    result = make_agent().compare("Plan my Saturday in Mumbai", ["jazz"])
    assert result["qloo"], "Qloo side must not be empty"
    assert result["generic"], "generic side must not be empty"
    assert result["qloo"][0].get("affinity") is not None
    assert "affinity" not in result["generic"][0]

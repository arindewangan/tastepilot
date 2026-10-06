"""Tests for demo_data.py — the simulated fixtures behind Demo Mode."""
from demo_data import (
    DEMO_GENERIC_LIST,
    DEMO_PLACE_INSIGHTS,
    demo_insights,
    demo_search,
    demo_tags,
)


def test_demo_search_matches_catalog():
    results = demo_search("murakami")
    assert results[0]["name"] == "Haruki Murakami"
    assert all(r["demo"] is True for r in results)


def test_demo_search_empty_query():
    assert demo_search("") == []


def test_demo_places_have_affinity_in_range():
    for place in DEMO_PLACE_INSIGHTS:
        assert 0 <= place["affinity"] <= 1
        assert place["name"]


def test_demo_insights_flags_everything():
    for item in demo_insights("urn:entity:place") + demo_insights("urn:entity:movie"):
        assert item["demo"] is True
        assert item["label"].startswith("Demo Mode")


def test_demo_insights_unknown_type_is_empty():
    assert demo_insights("urn:entity:podcast") == []


def test_demo_tags_lookup():
    found = demo_tags("cozy")
    assert found and found[0]["tag_id"] == "demo:tag:cozy"
    assert all(t["demo"] is True for t in found)


def test_demo_generic_list_has_four():
    assert len(DEMO_GENERIC_LIST) == 4

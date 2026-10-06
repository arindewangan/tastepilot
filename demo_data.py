"""Clearly-labeled SIMULATED data for TastePilot Demo Mode.

Everything in this file is fake/sample data used ONLY when QLOO_API_KEY (or
GEMINI_API_KEY) is not configured. Every consumer must surface the ``demo``
flag so the UI can label the surface as simulated. Never present these values
as real Qloo output.
"""

DEMO_FLAG = {"demo": True, "simulated": True, "label": "Demo Mode — simulated data"}

# ---------------------------------------------------------------------------
# Simulated taste-seed entities (what /search would resolve user favorites to)
# ---------------------------------------------------------------------------
DEMO_ENTITY_CATALOG = {
    "wes anderson": {
        "name": "Wes Anderson",
        "entity_id": "demo:entity:wes-anderson",
        "filter_type": "urn:entity:person",
        "affinity": None,
        "popularity": 0.94,
        "tags": ["quirky", "symmetrical", "indie film", "retro"],
    },
    "jazz": {
        "name": "Jazz",
        "entity_id": "demo:entity:jazz",
        "filter_type": "urn:entity:artist",
        "affinity": None,
        "popularity": 0.91,
        "tags": ["improvisation", "late night", "vinyl", "soulful"],
    },
    "murakami": {
        "name": "Haruki Murakami",
        "entity_id": "demo:entity:haruki-murakami",
        "filter_type": "urn:entity:book",
        "affinity": None,
        "popularity": 0.93,
        "tags": ["surreal", "introspective", "japanese literature", "dreamlike"],
    },
    "ramen": {
        "name": "Ramen",
        "entity_id": "demo:entity:ramen",
        "filter_type": "urn:entity:place",
        "affinity": None,
        "popularity": 0.88,
        "tags": ["japanese cuisine", "comfort food", "noodles"],
    },
    "anoushka shankar": {
        "name": "Anoushka Shankar",
        "entity_id": "demo:entity:anoushka-shankar",
        "filter_type": "urn:entity:artist",
        "affinity": None,
        "popularity": 0.82,
        "tags": ["indian classical", "sitar", "fusion"],
    },
    "satyajit ray": {
        "name": "Satyajit Ray",
        "entity_id": "demo:entity:satyajit-ray",
        "filter_type": "urn:entity:person",
        "affinity": None,
        "popularity": 0.89,
        "tags": ["bengali cinema", "arthouse", "humanist"],
    },
}

# ---------------------------------------------------------------------------
# Simulated /v2/insights results: music+film taste -> Mumbai places
# ---------------------------------------------------------------------------
DEMO_PLACE_INSIGHTS = [
    {
        "name": "Britannia & Co.",
        "entity_id": "demo:place:britannia",
        "affinity": 0.91,
        "popularity": 0.88,
        "tags": ["heritage", "irani café", "comfort food"],
        "location": {"city": "Mumbai", "area": "Fort"},
    },
    {
        "name": "Kala Ghoda Arts Precinct",
        "entity_id": "demo:place:kala-ghoda",
        "affinity": 0.87,
        "popularity": 0.93,
        "tags": ["art galleries", "indie", "walkable"],
        "location": {"city": "Mumbai", "area": "Kala Ghoda"},
    },
    {
        "name": "Blue Tokai — Kala Ghoda",
        "entity_id": "demo:place:blue-tokai",
        "affinity": 0.84,
        "popularity": 0.86,
        "tags": ["specialty coffee", "slow mornings", "bookish"],
        "location": {"city": "Mumbai", "area": "Kala Ghoda"},
    },
    {
        "name": "Prithvi Theatre",
        "entity_id": "demo:place:prithvi",
        "affinity": 0.83,
        "popularity": 0.90,
        "tags": ["live theatre", "indie", "cultural hub"],
        "location": {"city": "Mumbai", "area": "Juhu"},
    },
    {
        "name": "Taj Mahal Tea House",
        "entity_id": "demo:place:tea-house",
        "affinity": 0.79,
        "popularity": 0.81,
        "tags": ["heritage", "quiet", "conversation"],
        "location": {"city": "Mumbai", "area": "Bandra"},
    },
    {
        "name": "The Daily — All Day Café",
        "entity_id": "demo:place:the-daily",
        "affinity": 0.76,
        "popularity": 0.84,
        "tags": ["brunch", "design-forward", "casual"],
        "location": {"city": "Mumbai", "area": "Bandra"},
    },
]

# ---------------------------------------------------------------------------
# Simulated /v2/insights results: second cross-domain leg -> movies
# ---------------------------------------------------------------------------
DEMO_MOVIE_INSIGHTS = [
    {
        "name": "The Lunchbox",
        "entity_id": "demo:movie:lunchbox",
        "affinity": 0.88,
        "popularity": 0.85,
        "tags": ["mumbai", "introspective", "arthouse"],
    },
    {
        "name": "The Grand Budapest Hotel",
        "entity_id": "demo:movie:grand-budapest",
        "affinity": 0.86,
        "popularity": 0.95,
        "tags": ["quirky", "symmetrical", "indie film"],
    },
    {
        "name": "Pather Panchali",
        "entity_id": "demo:movie:pather-panchali",
        "affinity": 0.81,
        "popularity": 0.87,
        "tags": ["bengali cinema", "humanist", "classic"],
    },
]

# ---------------------------------------------------------------------------
# Simulated /v2/tags results
# ---------------------------------------------------------------------------
DEMO_TAG_CATALOG = {
    "cozy": {"name": "cozy", "tag_id": "demo:tag:cozy"},
    "izakaya": {"name": "izakaya", "tag_id": "demo:tag:izakaya"},
    "heritage": {"name": "heritage", "tag_id": "demo:tag:heritage"},
    "late night": {"name": "late night", "tag_id": "demo:tag:late-night"},
    "low-key": {"name": "low-key", "tag_id": "demo:tag:low-key"},
    "vegetarian": {"name": "vegetarian", "tag_id": "demo:tag:vegetarian"},
    "live music": {"name": "live music", "tag_id": "demo:tag:live-music"},
    "art galleries": {"name": "art galleries", "tag_id": "demo:tag:art-galleries"},
}

# ---------------------------------------------------------------------------
# Canned "generic LLM" list for the Why-Qloo? A/B comparison (Demo Mode)
# ---------------------------------------------------------------------------
DEMO_GENERIC_LIST = [
    {"name": "Gateway of India", "why": "A popular tourist landmark."},
    {"name": "Juhu Beach", "why": "A well-known beach."},
    {"name": "Phoenix Mall food court", "why": "Lots of dining options."},
    {"name": "Marine Drive", "why": "A famous promenade."},
]

# ---------------------------------------------------------------------------
# Canned explanation templates (Demo Mode LLM narration)
# ---------------------------------------------------------------------------
WHY_TEMPLATES = [
    "Taste-graph match: fans of {seed} over-index on {tag}, which is why “{name}” scores {pct}% affinity for you.",
    "This pick is taste-grounded, not guessed: your {seed} signal transfers across domains to {tag} experiences — “{name}” at {pct}%.",
    "Qloo’s cross-domain graph connects your {seed} taste to {tag} culture; “{name}” lands at {pct}% affinity.",
]

GENERIC_PROFILE_SUMMARY = (
    "A cross-domain taste fingerprint weighted across music, film, food and "
    "places — built from your favorites and Qloo’s taste graph."
)


def _flagged(item):
    flagged = dict(item)
    flagged.update(DEMO_FLAG)
    return flagged


def demo_search(query):
    """Simulated /search: match the query against the demo entity catalog."""
    q = (query or "").strip().lower()
    if not q:
        return []
    return [_flagged(e) for key, e in DEMO_ENTITY_CATALOG.items() if q in key or key in q]


def demo_insights(filter_type, take=10):
    """Simulated /v2/insights for the two demo legs."""
    if filter_type == "urn:entity:place":
        return [_flagged(e) for e in DEMO_PLACE_INSIGHTS[: max(1, take)]]
    if filter_type in ("urn:entity:movie", "urn:entity:tv_show"):
        return [_flagged(e) for e in DEMO_MOVIE_INSIGHTS[: max(1, take)]]
    return []


def demo_tags(query):
    """Simulated /v2/tags lookup."""
    q = (query or "").strip().lower()
    if not q:
        return []
    return [
        dict(t, **DEMO_FLAG)
        for key, t in DEMO_TAG_CATALOG.items()
        if q in key or key in q
    ]

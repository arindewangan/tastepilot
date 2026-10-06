"""TastePilot's agentic core: a small ReAct-style agent framework.

Loop: plan (classify intent) -> act (Qloo tools) -> synthesize (Gemini narration).

Exposed tools (all Qloo traffic stays server-side; the key never reaches the
browser):
  - taste_search(query)   -> resolve favorites to Qloo entity IDs
  - taste_tags(query)     -> resolve descriptors to tag IDs
  - taste_insights(...)   -> cross-domain affinity-ranked recommendations

The agent emits a ``trace`` of thinking steps so the UI can show its work.
"""

import logging
import re

log = logging.getLogger(__name__)

CITY_HINTS = [
    "mumbai", "bengaluru", "bangalore", "delhi", "new delhi", "chennai",
    "hyderabad", "kolkata", "pune", "ahmedabad", "goa", "jaipur", "kochi",
]

MOOD_WORDS = ["cozy", "low-key", "low key", "romantic", "lively", "quiet",
              "late night", "vegetarian", "veg", "budget", "luxury", "artsy"]


class TastePilotAgent:
    def __init__(self, qloo_client, llm_client):
        self.qloo = qloo_client
        self.llm = llm_client

    # ------------------------------------------------------------------ plan
    def classify_intent(self, text):
        """Classify the user's ask into kind/location/moods. No network."""
        lowered = (text or "").lower()
        location = next((c.title() for c in CITY_HINTS if c in lowered), None)
        moods = [m for m in MOOD_WORDS if m in lowered]
        kind = "plan"
        if any(w in lowered for w in ["vs", "versus", "why qloo", "compare"]):
            kind = "compare"
        elif any(w in lowered for w in ["profile", "taste dna", "who am i"]):
            kind = "profile"
        budget = None
        match = re.search(r"(?:under|below|₹|rs\.?)\s?([\d,]+)", lowered)
        if match:
            budget = match.group(1).replace(",", "")
        return {
            "kind": kind,
            "location": location or "Mumbai",
            "moods": moods,
            "budget": budget,
            "raw": text,
        }

    # ------------------------------------------------------------------- act
    def taste_search(self, query):
        return self.qloo.search(query)

    def taste_tags(self, query):
        return self.qloo.tags(query)

    def taste_insights(self, filter_type, **kwargs):
        return self.qloo.insights(filter_type, **kwargs)

    # -------------------------------------------------------------- profile
    def build_taste_profile(self, favorites):
        """Resolve favorites -> entities -> cross-domain taste DNA."""
        trace = [{"step": "classify", "detail": f"Resolving {len(favorites)} taste seeds"}]
        entities, tag_weights, seed_ids = [], {}, []
        for fav in favorites:
            matches = self.taste_search(fav)
            trace.append({"step": "search", "detail": f"“{fav}” → {matches[0]['name'] if matches else 'no match'}"})
            if not matches:
                continue
            entity = matches[0]
            entities.append(entity)
            if entity.get("entity_id"):
                seed_ids.append(entity["entity_id"])
            for tag in entity.get("tags") or []:
                tag_weights[tag] = tag_weights.get(tag, 0) + 1

        demo = self.qloo.demo_mode
        profile_summary = self.llm.generate(
            "Write a 2-sentence taste DNA profile summary for someone who loves: "
            + ", ".join(e["name"] for e in entities)
        )
        dna = {
            "entities": entities,
            "tags": sorted(tag_weights, key=tag_weights.get, reverse=True)[:12],
            "tag_weights": tag_weights,
            "summary": profile_summary["text"],
            "demo": demo or profile_summary["demo"],
            "seed_ids": seed_ids,
        }
        trace.append({"step": "synthesize", "detail": "Taste DNA fingerprint composed"})
        return {"profile": dna, "trace": trace}

    # ------------------------------------------------------------------ plan
    def plan(self, request_text, favorites):
        """Full agent loop: intent -> Qloo cross-domain insights -> narrated plan."""
        intent = self.classify_intent(request_text)
        trace = [{"step": "classify",
                  "detail": f"Intent: {intent['kind']} · {intent['location']} · moods: {intent['moods'] or '—'}"}]

        profile_result = self.build_taste_profile(favorites)
        profile = profile_result["profile"]
        trace.extend(profile_result["trace"])
        seed_ids = profile["seed_ids"]
        seed_names = [e["name"] for e in profile["entities"]]

        # Resolve mood descriptors to tag IDs for signals.
        tag_ids = []
        for mood in intent["moods"]:
            found = self.taste_tags(mood)
            trace.append({"step": "tags", "detail": f"“{mood}” → {found[0]['name'] if found else 'no tag'}"})
            if found and found[0].get("tag_id"):
                tag_ids.append(found[0]["tag_id"])

        # Leg 1 (the irreplaceable moment): music/film taste -> places.
        places = self.taste_insights(
            "urn:entity:place",
            signal_entities=seed_ids or None,
            signal_tags=tag_ids or None,
            location=intent["location"],
            take=6,
        )
        trace.append({"step": "insights",
                      "detail": f"Cross-domain jump: {len(seed_ids)} taste seeds → "
                                f"{len(places)} {intent['location']} places, ranked by affinity"})

        # Leg 2: second domain leg (movie night to match the plan).
        movies = self.taste_insights(
            "urn:entity:movie",
            signal_entities=seed_ids or None,
            take=3,
        )
        trace.append({"step": "insights",
                      "detail": f"Second leg: {len(movies)} films matching the same taste"})

        items = []
        for place in places:
            items.append({
                "kind": "place",
                "name": place["name"],
                "affinity": place.get("affinity"),
                "popularity": place.get("popularity"),
                "tags": place.get("tags"),
                "location": place.get("location"),
                "why": self.llm.explain_pick(place, seed_names, demo_profile=profile["demo"]),
                "demo": place.get("demo", False),
            })
        for movie in movies:
            items.append({
                "kind": "movie",
                "name": movie["name"],
                "affinity": movie.get("affinity"),
                "popularity": movie.get("popularity"),
                "tags": movie.get("tags"),
                "why": self.llm.explain_pick(movie, seed_names, demo_profile=profile["demo"]),
                "demo": movie.get("demo", False),
            })

        demo = self.qloo.demo_mode
        return {
            "intent": intent,
            "profile": profile,
            "items": items,
            "trace": trace,
            "demo": demo,
        }

    # --------------------------------------------------------------- compare
    def compare(self, request_text, favorites):
        """Why-Qloo? A/B: generic-LLM list vs Qloo-grounded list, side by side."""
        plan_result = self.plan(request_text, favorites)
        generic = self.llm.generic_recommendations(request_text)
        return {
            "qloo": plan_result["items"],
            "generic": generic,
            "trace": plan_result["trace"],
            "demo": plan_result["demo"],
        }

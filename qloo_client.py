"""Qloo API client for TastePilot — the single module all Qloo traffic flows through.

- Base URL: https://hackathon.api.qloo.com (hackathon keys 401 on prod/staging)
- Auth: ``X-Api-Key`` request header (NOT Bearer, NOT query param)
- Only GET endpoints used: /search, /v2/tags, /v2/insights (POST only for
  complex JSON bodies; /recs and /recommendations are unsupported — do not use)
- Retries with backoff on 429; server-side cache for /search and /v2/tags
- Invalid ``filter.type`` values raise ValueError instead of hitting the API
  (Qloo silently ignores invalid params and returns empty results otherwise)
- When QLOO_API_KEY is unset, every method serves clearly-labeled Demo Mode
  data so judges always get a full click-through.
"""

import logging
import time

import requests

from demo_data import demo_insights, demo_search, demo_tags

log = logging.getLogger(__name__)

HACKATHON_BASE_URL = "https://hackathon.api.qloo.com"

ALLOWED_FILTER_TYPES = frozenset(
    {
        "urn:entity:artist",
        "urn:entity:book",
        "urn:entity:brand",
        "urn:entity:destination",
        "urn:entity:movie",
        "urn:entity:person",
        "urn:entity:place",
        "urn:entity:podcast",
        "urn:entity:tv_show",
        "urn:entity:video_game",
    }
)


class QlooAPIError(Exception):
    """Raised when a live Qloo request fails."""


class QlooClient:
    def __init__(self, api_key=None, base_url=HACKATHON_BASE_URL, timeout=15):
        self.api_key = (api_key or "").strip()
        self.base_url = (base_url or HACKATHON_BASE_URL).rstrip("/")
        self.timeout = timeout
        self._cache = {}
        if self.base_url != HACKATHON_BASE_URL:
            log.warning(
                "Qloo base URL is %s — hackathon keys only work on %s",
                self.base_url,
                HACKATHON_BASE_URL,
            )

    # ------------------------------------------------------------------ state
    @property
    def demo_mode(self):
        """True when no API key is configured; all calls return simulated data."""
        return not bool(self.api_key)

    def _headers(self):
        return {"X-Api-Key": self.api_key, "Accept": "application/json"}

    # ------------------------------------------------------------------ http
    def _get(self, path, params, retries=3):
        cache_key = (path, tuple(sorted((k, str(v)) for k, v in params.items())))
        if path in ("/search", "/v2/tags") and cache_key in self._cache:
            return self._cache[cache_key]

        url = self.base_url + path
        last_error = None
        for attempt in range(retries):
            try:
                resp = requests.get(
                    url, headers=self._headers(), params=params, timeout=self.timeout
                )
            except requests.RequestException as exc:  # network blip: back off
                last_error = exc
                time.sleep(1.5 * (attempt + 1))
                continue
            if resp.status_code == 429:  # rate limited: back off and retry
                last_error = QlooAPIError("429 rate limited")
                time.sleep(2 ** (attempt + 1))
                continue
            if resp.status_code == 401:
                raise QlooAPIError(
                    "401 Unauthorized — check QLOO_API_KEY and confirm the key "
                    "targets https://hackathon.api.qloo.com (keys 401 on prod/staging)."
                )
            if not resp.ok:
                raise QlooAPIError(f"Qloo request failed with status {resp.status_code}")
            try:
                data = resp.json()
            except ValueError as exc:
                raise QlooAPIError(f"Qloo returned non-JSON response: {exc}")
            if path in ("/search", "/v2/tags"):
                self._cache[cache_key] = data
            return data
        raise QlooAPIError(f"Qloo request failed after {retries} retries: {last_error}")

    # ----------------------------------------------------------------- parse
    @staticmethod
    def parse_entities(payload):
        """Normalize an /v2/insights payload to a flat list of entity dicts."""
        entities = []
        for raw in (payload or {}).get("entities", []) or []:
            tags = []
            for tag in raw.get("tags") or []:
                tags.append(tag.get("name") if isinstance(tag, dict) else tag)
            entities.append(
                {
                    "name": raw.get("name"),
                    "entity_id": raw.get("entity_id"),
                    "affinity": raw.get("affinity"),
                    "popularity": raw.get("popularity"),
                    "tags": [t for t in tags if t],
                    "location": raw.get("location") or {},
                    "demo": False,
                }
            )
        return entities

    # -------------------------------------------------------------- endpoints
    def search(self, query, types=None):
        """Resolve a human name ("Wes Anderson", "ramen") to Qloo entity IDs."""
        if self.demo_mode:
            return demo_search(query)
        params = {"query": query}
        if types:
            params["types"] = ",".join(types)
        payload = self._get("/search", params)
        results = []
        for raw in payload.get("results", []) or []:
            results.append(
                {
                    "name": raw.get("name"),
                    "entity_id": raw.get("entity_id"),
                    "affinity": None,
                    "popularity": raw.get("popularity"),
                    "tags": [],
                    "location": {},
                    "demo": False,
                }
            )
        return results

    def tags(self, query):
        """Resolve a descriptor ("cozy", "izakaya") to tag IDs."""
        if self.demo_mode:
            return demo_tags(query)
        payload = self._get("/v2/tags", {"filter.query": query})
        return [
            {"name": t.get("name"), "tag_id": t.get("tag_id"), "demo": False}
            for t in payload.get("tags", []) or []
        ]

    def insights(self, filter_type, signal_entities=None, signal_tags=None,
                 location=None, tag_filter=None, take=10):
        """The cross-domain engine: rank entities of ``filter_type`` by taste.

        Signals = what the user likes (entity/tag IDs). Filters = hard
        constraints (location, tag). Qloo silently ignores invalid params and
        returns empty results, so we validate ``filter_type`` up front.
        """
        if filter_type not in ALLOWED_FILTER_TYPES:
            raise ValueError(
                f"Invalid filter.type {filter_type!r}; must be one of "
                f"{sorted(ALLOWED_FILTER_TYPES)}"
            )
        if self.demo_mode:
            return demo_insights(filter_type, take=take)

        params = {"filter.type": filter_type, "take": max(1, min(take, 100))}
        if signal_entities:
            params["signal.interests.entities"] = ",".join(signal_entities)
        if signal_tags:
            params["signal.interests.tags"] = ",".join(signal_tags)
        if location:
            params["filter.location.query"] = location
        if tag_filter:
            params["filter.tags"] = tag_filter
        payload = self._get("/v2/insights", params)
        entities = self.parse_entities(payload)
        if not entities:
            log.info(
                "Qloo returned zero entities for %s — likely an ignored/invalid "
                "param combination; check the Entity Type Parameter Guide.",
                filter_type,
            )
        return entities

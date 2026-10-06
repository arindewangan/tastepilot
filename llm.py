"""Gemini (free tier) client for TastePilot narration.

- Uses the free Google AI Studio tier via GEMINI_API_KEY (no card required).
- Key is never sent to the browser; all calls are server-side.
- When GEMINI_API_KEY is unset, every method returns clearly-labeled
  canned "Demo Mode" narration so the app never blocks on the LLM.
"""

import logging

import requests

from demo_data import DEMO_GENERIC_LIST, WHY_TEMPLATES

log = logging.getLogger(__name__)

GEMINI_MODEL = "gemini-2.0-flash"
GENERATE_URL = (
    f"https://generativelanguage.googleapis.com/v1beta/models/"
    f"{GEMINI_MODEL}:generateContent"
)


class LLMError(Exception):
    """Raised when a live Gemini request fails."""


class GeminiClient:
    def __init__(self, api_key=None, model=GEMINI_MODEL, timeout=20):
        self.api_key = (api_key or "").strip()
        self.model = model or GEMINI_MODEL
        self.timeout = timeout

    @property
    def demo_mode(self):
        return not bool(self.api_key)

    def generate(self, prompt, system=None):
        """Return {"text": str, "demo": bool} — never raises for missing keys."""
        if self.demo_mode:
            return {"text": self._canned(prompt), "demo": True}
        body = {"contents": [{"parts": [{"text": prompt}]}]}
        if system:
            body["system_instruction"] = {"parts": [{"text": system}]}
        try:
            resp = requests.post(
                GENERATE_URL,
                params={"key": self.api_key},
                json=body,
                timeout=self.timeout,
            )
            if not resp.ok:
                raise LLMError(f"Gemini request failed: {resp.status_code}")
            data = resp.json()
            parts = (
                data.get("candidates", [{}])[0]
                .get("content", {})
                .get("parts", [])
            )
            text = "".join(p.get("text", "") for p in parts).strip()
            if not text:
                raise LLMError("Gemini returned an empty response")
            return {"text": text, "demo": False}
        except (requests.RequestException, LLMError) as exc:
            log.warning("Gemini call failed (%s); falling back to Demo Mode text", exc)
            return {"text": self._canned(prompt), "demo": True}

    # ------------------------------------------------------------ demo mode
    def _canned(self, prompt):
        """Deterministic, clearly-labeled narration when no key is configured."""
        lowered = (prompt or "").lower()
        if "taste dna" in lowered or "profile summary" in lowered:
            return (
                "[Demo Mode — simulated narration] Your taste fingerprint blends "
                "indie-film quirk, late-night jazz warmth, and introspective "
                "literary depth — Qloo's taste graph reads that as a pull toward "
                "heritage spaces, slow cafés, and arthouse culture."
            )
        return (
            "[Demo Mode — simulated narration] Grounded in your taste signals, "
            "this pick was ranked by affinity across Qloo's cultural graph — "
            "not by generic popularity."
        )

    def explain_pick(self, item, seed_names, demo_profile=False):
        """One-line 'why this fits your taste' for an itinerary item."""
        if self.demo_mode or demo_profile:
            name = item.get("name", "this pick")
            tags = item.get("tags") or ["cultural depth"]
            seed = seed_names[0] if seed_names else "your favorites"
            pct = int(round((item.get("affinity") or 0.8) * 100))
            template = WHY_TEMPLATES[hash(name) % len(WHY_TEMPLATES)]
            return "[Demo Mode — simulated] " + template.format(
                seed=seed, tag=tags[0], name=name, pct=pct
            )
        prompt = (
            "You are TastePilot, a cultural concierge. In ONE sentence, explain "
            f"why '{item.get('name')}' (tags: {', '.join(item.get('tags') or [])}) "
            f"fits someone whose taste seeds are {', '.join(seed_names)}. "
            "Be specific and warm; no more than 25 words."
        )
        return self.generate(prompt)["text"]

    def generic_recommendations(self, request_text):
        """The 'generic LLM' side of the Why-Qloo? comparison — no Qloo input."""
        if self.demo_mode:
            return [dict(item, demo=True) for item in DEMO_GENERIC_LIST]
        prompt = (
            "List 4 generic tourist recommendations for: "
            f"{request_text}. Return each as 'Name — one-line why'. No taste data "
            "about the user is available; answer from general knowledge."
        )
        text = self.generate(prompt)["text"]
        items = []
        for line in text.splitlines():
            line = line.strip().lstrip("-•*1234567890. ")
            if not line:
                continue
            name, _, why = line.partition("—")
            name, _, why = name.partition("-")
            items.append({"name": name.strip(), "why": why.strip(), "demo": False})
            if len(items) == 4:
                break
        return items

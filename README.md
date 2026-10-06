# TastePilot — an agentic cultural concierge powered by Qloo

**Tell it what you love; it plans your life around your taste** — grounded in Qloo's 250M+ entity taste graph, not LLM guesswork.

Built for the [Qloo Agentic Hackathon](https://qloo.devpost.com/) ("Agents, but with taste").

## The 60-second loop

1. **Tell it what you love** — type 3–6 favorites across domains ("Wes Anderson, jazz, Murakami, ramen"). Each resolves to a Qloo entity ID via `GET /search`.
2. **Get your Taste DNA** — the agent builds a cross-domain taste fingerprint (affinity-weighted tags across music/film/food/places), rendered as an animated radar.
3. **Ask for a plan** — "Plan my Saturday in Mumbai". The agent classifies intent → fires the **cross-domain jump** (`GET /v2/insights`: your film+music taste → Mumbai places, ranked by `affinity` 0–1) → a second leg (films to match) → Gemini narrates every pick with a one-line "why this fits your taste".
4. **The "Why Qloo?" toggle** — side-by-side: generic-LLM recommendations vs Qloo-grounded ones. Visible proof the product is not the same without Qloo.
5. **Iterate conversationally** — "more low-key", "vegetarian", "near Bandra" re-queries with refined signals/filters.

## Why it's Qloo-irreplaceable

- `GET /search` — favorites → entity IDs (the taste seeds)
- `GET /v2/tags` — mood/cuisine descriptors → tag IDs for signals
- `GET /v2/insights?filter.type=urn:entity:place&signal.interests.entities=…&filter.location.query=Mumbai` — **the cross-domain jump**, music/film taste → restaurants/venues, affinity-ranked
- `GET /v2/insights?filter.type=urn:entity:movie` — second domain leg

All Qloo calls are server-side (`qloo_client.py`); the key never reaches the browser.

## Run it

```bash
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in keys (optional — Demo Mode works without them)
python app.py          # http://localhost:5000
```

| Env var | Purpose |
|---|---|
| `QLOO_API_KEY` | Qloo hackathon key (request via the developer-guide form). Valid **only** on `https://hackathon.api.qloo.com`. |
| `GEMINI_API_KEY` | Google AI Studio free-tier key for narration (optional). |

**Demo Mode:** with no keys set, every surface serves clearly-labeled simulated data, so judges get a full click-through end-to-end. Set the keys and the live path activates automatically — no code changes.

## Tests

```bash
./venv/bin/python -m pytest tests/ -q   # 38 tests, zero network
```

## Layout

```
tastepilot/
  app.py            Flask app + routes (/api/taste-profile, /api/plan, /api/compare, /api/health)
  qloo_client.py    Single Qloo client: X-Api-Key, hackathon base URL, 429 backoff, caching, Demo Mode
  agent.py          ReAct-style agent: classify → taste_search/taste_tags/taste_insights → synthesize
  llm.py            Gemini free-tier client with env gating + labeled canned fallback
  demo_data.py      Clearly-labeled simulated fixtures for Demo Mode
  static/index.html Polished single-page app (chips, Taste DNA radar, chat, affinity bars, Why-Qloo toggle)
  demo/index.html   Standalone Pages-ready simulated showcase of the full user loop
  assets/           logo.webp + banner.png (AI-generated)
  tests/            38 mocked pytest tests
```

## License

MIT — see [LICENSE](LICENSE).

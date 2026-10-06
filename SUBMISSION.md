# TastePilot — Devpost submission draft

> Fill in the TBD links once the pipeline ships (GitHub push, live demo deploy, optional video).

## Title
TastePilot — an agentic cultural concierge powered by Qloo

## Tagline
Tell it what you love; it plans your life around your taste — grounded in 250M+ cultural entities, not LLM guesswork.

## Description

**Problem.** LLM recommenders hallucinate and can't model taste. Single-domain apps (Spotify Wrapped, Tastebuds) never cross domains — your music taste never picks your restaurant.

**Solution.** TastePilot is a conversational agent that resolves your favorites to Qloo entities (`/search`), builds a cross-domain Taste DNA fingerprint, then fires cross-domain `GET /v2/insights` queries — your *film + music taste → Mumbai restaurants and venues*, ranked by Qloo's `affinity` score (0–1). Every pick in the generated itinerary carries an affinity bar and a one-line "why this fits your taste," narrated by Gemini (free tier). Ask "plan my Saturday in Mumbai" and watch the agent think: classify → search the taste graph → rank places → compose.

**Why it's Qloo-powered (not the same without Qloo).** The "Why Qloo?" toggle shows a side-by-side A/B: generic-LLM recommendations vs Qloo-grounded ones for the same request. The taste transfer — Wes Anderson + jazz → a 91%-affinity heritage Irani café — is computed by Qloo's signal+filter taste graph; no LLM could derive it. All Qloo calls run server-side, with 429 backoff and response caching, and the app ships an honestly-labeled Demo Mode fallback so the full loop always works while API keys are provisioned.

**Real-world path.** Match Group's Yuzu proved Qloo taste data moves metrics (+70% likes). TastePilot takes the same proven taste graph and gives it agency: a concierge planning layer for hospitality, travel, and live-experience businesses (think Live Nation: gigs + dinner + late-night, all taste-matched).

**Built with:** Python (Flask), vanilla JS, Qloo Taste AI API (`/search`, `/v2/tags`, `/v2/insights`), Google Gemini, MIT license.

## Links
- Demo (live, externally hosted): https://arindewangan.github.io/tastepilot/demo/ (simulated showcase; live app runs the same loop against https://hackathon.api.qloo.com)
- Code repo (public, MIT): https://github.com/arindewangan/tastepilot
- Demo video: **TBD** (not required by rules; optional)

## Built with
Python (Flask) · JavaScript · Qloo Taste AI API · Google Gemini · Tailwind-style CSS

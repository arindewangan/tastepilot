"""TastePilot — Flask backend for the Qloo Agentic Hackathon.

Serves the single-page app and JSON API. All Qloo and Gemini traffic is
server-side; API keys live only in environment variables.

Routes:
  GET  /                  -> the app
  GET  /api/health        -> {status, demo_mode, has_qloo_key, has_gemini_key}
  POST /api/taste-profile -> {favorites: [...]} -> taste DNA profile
  POST /api/plan          -> {request, favorites: [...]} -> narrated itinerary
  POST /api/compare       -> {request, favorites: [...]} -> Why-Qloo? A/B
"""

import logging
import os

from flask import Flask, jsonify, request, send_from_directory

from agent import TastePilotAgent
from llm import GeminiClient
from qloo_client import QlooClient

log = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def build_app():
    app = Flask(__name__, static_folder=os.path.join(BASE_DIR, "static"))

    qloo = QlooClient(api_key=os.environ.get("QLOO_API_KEY"))
    llm = GeminiClient(api_key=os.environ.get("GEMINI_API_KEY"))
    agent = TastePilotAgent(qloo, llm)

    @app.get("/")
    def index():
        return send_from_directory(app.static_folder, "index.html")

    @app.get("/api/health")
    def health():
        return jsonify(
            {
                "status": "ok",
                "demo_mode": qloo.demo_mode,
                "has_qloo_key": bool(qloo.api_key),
                "has_gemini_key": bool(llm.api_key),
                "qloo_base": qloo.base_url,
            }
        )

    def _favorites(payload):
        favs = payload.get("favorites") or []
        if not isinstance(favs, list) or not favs:
            return None
        return [str(f).strip() for f in favs if str(f).strip()][:12]

    @app.post("/api/taste-profile")
    def taste_profile():
        payload = request.get_json(silent=True) or {}
        favs = _favorites(payload)
        if not favs:
            return jsonify({"error": "Provide 'favorites' as a non-empty list."}), 400
        return jsonify(agent.build_taste_profile(favs))

    @app.post("/api/plan")
    def plan():
        payload = request.get_json(silent=True) or {}
        favs = _favorites(payload)
        req_text = (payload.get("request") or "").strip()
        if not favs or not req_text:
            return (
                jsonify({"error": "Provide 'request' (string) and 'favorites' (list)."}),
                400,
            )
        return jsonify(agent.plan(req_text, favs))

    @app.post("/api/compare")
    def compare():
        payload = request.get_json(silent=True) or {}
        favs = _favorites(payload)
        req_text = (payload.get("request") or "").strip()
        if not favs or not req_text:
            return (
                jsonify({"error": "Provide 'request' (string) and 'favorites' (list)."}),
                400,
            )
        return jsonify(agent.compare(req_text, favs))

    return app


app = build_app()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)

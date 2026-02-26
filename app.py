import os
import json
from typing import Any, Dict, List, Optional

from flask import Flask, render_template, jsonify
import yaml

APP_NAME = "WizardWebb"

DEFAULT_LINKS_FILE = os.path.join(os.path.dirname(__file__), "data", "links.yml")

def load_links(path: str) -> List[Dict[str, Any]]:
    """Load link items from a YAML file."""
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or []
    if not isinstance(data, list):
        raise ValueError("links.yml must contain a YAML list of items.")
    # Normalize
    out: List[Dict[str, Any]] = []
    for i, item in enumerate(data):
        if not isinstance(item, dict):
            continue
        out.append({
            "id": item.get("id") or f"item_{i+1}",
            "name": str(item.get("name", "")).strip(),
            "url": (str(item.get("url")).strip() if item.get("url") else None),
            "description": str(item.get("description", "")).strip(),
            "category": str(item.get("category", "Other")).strip() or "Other",
            "tags": item.get("tags") or [],
            "status": str(item.get("status", "ok")).strip().lower(),
            "note": str(item.get("note", "")).strip(),
        })
    # Basic validation
    for it in out:
        if not it["name"]:
            it["name"] = "(Unnamed)"
        if not isinstance(it["tags"], list):
            it["tags"] = [str(it["tags"])]
    return out

def unique_categories(links: List[Dict[str, Any]]) -> List[str]:
    cats = sorted({(l.get("category") or "Other") for l in links})
    # Put "All" is handled in UI; keep user-facing ordering nice:
    preferred = ["Search", "Research", "OSINT", "Security & Privacy", "Web Tools", "Freebies & Deals", "Other"]
    ordered = []
    for p in preferred:
        if p in cats:
            ordered.append(p)
    for c in cats:
        if c not in ordered:
            ordered.append(c)
    return ordered

def create_app() -> Flask:
    app = Flask(__name__)

    links_file = os.environ.get("LINKS_FILE", DEFAULT_LINKS_FILE)
    links = load_links(links_file)
    categories = unique_categories(links)

    @app.get("/")
    def index():
        return render_template(
            "index.html",
            app_name=APP_NAME,
            links=links,
            categories=categories,
            links_file=os.path.relpath(links_file, os.path.dirname(__file__)),
        )

    @app.get("/about")
    def about():
        return render_template("about.html", app_name=APP_NAME)

    @app.get("/api/links")
    def api_links():
        return jsonify({"app": APP_NAME, "count": len(links), "links": links})

    @app.get("/healthz")
    def healthz():
        return jsonify({"ok": True})

    return app

app = create_app()

if __name__ == "__main__":
    if os.environ.get("STREAMLIT_SERVER_PORT") or os.environ.get("STREAMLIT_SERVER_HEADLESS"):
        print("Detected Streamlit runtime; not starting Flask server. Use streamlit_app.py instead.")
    else:
        port = int(os.environ.get("PORT", "8000"))
        app.run(host="0.0.0.0", port=port, debug=False)

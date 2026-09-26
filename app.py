"""
app.py — Person 2's work (Backend)

A small Flask API that:
  - accepts new complaints from the frontend form (POST /api/complaints)
  - runs them through the AI engine (ai_engine.analyze_complaint)
  - stores results in memory (swap for a real DB later — see note below)
  - serves the results to the dashboard (GET /api/complaints)
  - serves aggregate counts for the charts (GET /api/analytics)

Run it with:
    pip install -r requirements.txt
    python app.py
Then open frontend/index.html (or dashboard.html) in your browser.
"""

from flask import Flask, jsonify, request
from flask_cors import CORS

import ai_engine
from sample_data import SAMPLE_COMPLAINTS

app = Flask(__name__)
CORS(app)  # allow the static frontend (opened as a file / different port) to call this API

# In-memory "database". Swap this list for a real DB (SQLite/Postgres) when
# you're ready — every place that touches it is marked below.
COMPLAINTS: list[dict] = []
_next_id = 1


def _seed():
    """Pre-load a few sample complaints so the dashboard isn't empty on first run."""
    global _next_id
    for item in SAMPLE_COMPLAINTS:
        result = ai_engine.analyze_complaint(item["text"], item["customer"], item["order_id"])
        result["id"] = _next_id
        COMPLAINTS.append(result)
        _next_id += 1


@app.route("/api/complaints", methods=["POST"])
def create_complaint():
    """Person 3 (Frontend) posts here from the complaint form."""
    global _next_id
    data = request.get_json(force=True) or {}
    text = (data.get("text") or "").strip()
    if not text:
        return jsonify({"error": "Complaint text is required."}), 400

    result = ai_engine.analyze_complaint(
        text=text,
        customer=data.get("customer"),
        order_id=data.get("order_id"),
    )
    result["id"] = _next_id
    _next_id += 1
    COMPLAINTS.append(result)  # <- swap for db.session.add(...) / INSERT later
    return jsonify(result), 201


@app.route("/api/complaints", methods=["GET"])
def list_complaints():
    """Person 3 (Frontend) polls here to populate the dashboard table."""
    ordered = sorted(COMPLAINTS, key=lambda c: c["id"], reverse=True)
    return jsonify(ordered)


@app.route("/api/analytics", methods=["GET"])
def analytics():
    """Aggregate counts for the dashboard charts."""
    by_category: dict[str, int] = {}
    by_urgency: dict[str, int] = {}
    by_department: dict[str, int] = {}

    for c in COMPLAINTS:
        by_category[c["category"]] = by_category.get(c["category"], 0) + 1
        by_urgency[c["urgency"]] = by_urgency.get(c["urgency"], 0) + 1
        by_department[c["department"]] = by_department.get(c["department"], 0) + 1

    return jsonify({
        "total": len(COMPLAINTS),
        "high_urgency": by_urgency.get("High", 0),
        "by_category": by_category,
        "by_urgency": by_urgency,
        "by_department": by_department,
    })


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    _seed()
    app.run(debug=True, port=5000)

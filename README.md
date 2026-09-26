# AI Customer Support System

A complaint automatically gets **categorized, scored for urgency, summarized,
routed to a department, and answered with a drafted reply** — all in real time.

```
Customer submits a complaint
        │
        ▼
 ai_engine.py  →  category, urgency, summary, department, reply
        │
        ▼
   app.py (Flask API)  →  stores it, serves it
        │
        ▼
 index.html / dashboard.html  →  submission form + live results dashboard
```

## Example

**Input**
> "I ordered my laptop 8 days ago. It was supposed to arrive on Monday but the tracking hasn't changed for 4 days."

**Output**

| Field | Value |
|---|---|
| Category | Delivery |
| Urgency | High |
| Summary | Laptop delivery is delayed and tracking hasn't updated. |
| Department | Logistics |
| Suggested action | Investigate courier status. |
| Reply | Auto-drafted, empathetic, professional |

## Repository layout

```
ai-customer-support/
├── backend/
│   ├── ai_engine.py       # Person 1 (AI/LLM) — categorize, urgency, summarize, reply, route
│   ├── app.py             # Person 2 (Backend) — Flask API
│   ├── sample_data.py     # Person 4 (Data & Testing) — sample complaints + rules
│   └── requirements.txt
├── frontend/
│   ├── index.html         # Person 3 (Frontend) — complaint intake form
│   ├── dashboard.html     # Person 3 (Frontend) — results dashboard
│   ├── style.css
│   └── script.js
├── tests/
│   └── test_ai_engine.py  # Person 4 (Data & Testing) — automated scenario tests
└── README.md
```

## How to run it

**1. Backend**
```bash
cd backend
pip install -r requirements.txt
python app.py
```
This starts the API at `http://localhost:5000` and seeds it with sample complaints
from `sample_data.py` so the dashboard isn't empty on first load.

**2. Frontend**
Just open `frontend/index.html` in your browser (no build step). Submit a
complaint, then click "Dashboard" to see it — and every seeded sample — laid out
with category/urgency charts.

**3. Tests**
```bash
python tests/test_ai_engine.py
```

## Team split (who owns what)

| Person | Area | Files |
|---|---|---|
| 1 | AI / LLM — prompt engineering, complaint analysis, reply generation | `backend/ai_engine.py` |
| 2 | Backend — API, connecting AI to the app | `backend/app.py` |
| 3 | Frontend — complaint input page, results dashboard, UI | `frontend/*` |
| 4 | Data & Testing — sample complaints, category/priority rules, scenario tests, analytics | `backend/sample_data.py`, `tests/test_ai_engine.py` |

The pieces only talk through two contracts, so each person can build in
parallel:
- **Person 1 → Person 2**: `ai_engine.analyze_complaint(text, customer, order_id)` returns one dict with every field the frontend needs.
- **Person 2 → Person 3**: the API exposes `POST /api/complaints`, `GET /api/complaints`, `GET /api/analytics`.

## Swapping in a real LLM

`ai_engine.py` ships with fast, free, keyword-based logic so the whole team can
demo it instantly. When you're ready for real reasoning, `analyze_with_llm()`
in the same file is a drop-in replacement with the exact same output shape —
just set `ANTHROPIC_API_KEY` in your environment and change one line in
`app.py`:

```python
result = ai_engine.analyze_with_llm(text, customer, order_id)  # instead of analyze_complaint
```

## Dashboard feature (the extra one)

`dashboard.html` is the "one feature I'd add": a live view of every complaint
the AI has processed, with:
- a stat strip (total complaints, how many are high-urgency, categories/departments involved)
- a sortable-by-recency table of every complaint and its AI-generated fields
- two bar charts (by category, by urgency) built with no external chart library

It's already wired into the same API as the intake form, so nothing extra
needs to run.

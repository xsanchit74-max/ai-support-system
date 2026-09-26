"""
ai_engine.py — Person 1's work (AI / LLM)

This module is the "brain" of the system. Given a raw complaint, it:
  1. Categorizes it            -> categorize()
  2. Detects urgency            -> detect_urgency()
  3. Summarizes it              -> summarize()
  4. Suggests a department      -> route_department()
  5. Generates a reply          -> generate_reply()

Everything here runs on fast, transparent keyword/rule logic by default
(so the whole team can demo the system with zero API keys or cost).
If you want real LLM reasoning instead, flip on the Claude-powered path
at the bottom (analyze_with_llm) — it's a drop-in replacement for
analyze_complaint() and uses the exact same output shape, so nothing
else in the app has to change.
"""

import os
import re
from datetime import datetime, timezone

# ---------------------------------------------------------------------------
# 1. CATEGORIES — Person 4 owns the *content* of these rules (edit freely),
#    Person 1 owns the *engine* that applies them.
# ---------------------------------------------------------------------------

CATEGORY_KEYWORDS = {
    "Delivery": [
        "delivery", "deliver", "shipping", "shipped", "tracking", "courier",
        "dispatch", "package hasn't", "parcel", "still hasn't arrived",
        "late", "delayed", "delay", "hasn't come", "not received", "lost",
        "when will my order arrive", "where is my order",
    ],
    "Billing": [
        "refund", "charge", "charged", "invoice", "payment", "billing",
        "money", "price", "overcharged", "double charged", "subscription",
        "cancel my order", "transaction",
    ],
    "Product Quality": [
        "broken", "damage", "damaged", "defective", "scratch", "crack",
        "cracked", "doesn't work", "not working", "stopped working",
        "faulty", "dead on arrival", "dent",
    ],
    "Account": [
        "password", "login", "log in", "account", "locked out", "sign in",
        "otp", "verification", "reset my", "can't access",
    ],
    "General Inquiry": [
        "how do i", "question", "wondering", "just asking", "when will",
        "information", "details about",
    ],
}

DEPARTMENT_BY_CATEGORY = {
    "Delivery": "Logistics",
    "Billing": "Finance",
    "Product Quality": "Returns & Warranty",
    "Account": "Technical Support",
    "General Inquiry": "Customer Support",
}

SUGGESTED_ACTION = {
    "Delivery": "Investigate courier / tracking status and provide an updated ETA.",
    "Billing": "Review the transaction and confirm charge/refund status with Finance.",
    "Product Quality": "Open a warranty/return case and arrange inspection or replacement.",
    "Account": "Verify identity and assist with account/password recovery.",
    "General Inquiry": "Provide the requested information or route to the right specialist.",
}

# ---------------------------------------------------------------------------
# 2. URGENCY — simple weighted keyword scoring (0-2 low, 3-4 medium, 5+ high)
# ---------------------------------------------------------------------------

URGENCY_KEYWORDS = {
    "high": [
        "urgent", "asap", "immediately", "emergency", "furious", "angry",
        "unacceptable", "worst", "scam", "fraud", "lawyer", "legal",
        "refund now", "cancel my account", "never again", "8 days",
        "week", "still hasn't", "no response", "ignored",
    ],
    "medium": [
        "disappointed", "frustrated", "concerned", "please help",
        "could you help", "waiting", "still waiting", "delayed", "not happy",
    ],
}

EXCLAIM_WEIGHT = 1  # each extra "!" beyond the first adds urgency weight


def _count_hits(text: str, keywords: list[str]) -> int:
    return sum(1 for kw in keywords if kw in text)


def categorize(text: str) -> str:
    text_l = text.lower()
    scores = {cat: _count_hits(text_l, kws) for cat, kws in CATEGORY_KEYWORDS.items()}
    best_cat = max(scores, key=scores.get)
    if scores[best_cat] == 0:
        return "General Inquiry"
    return best_cat


def detect_urgency(text: str) -> str:
    text_l = text.lower()
    high_hits = _count_hits(text_l, URGENCY_KEYWORDS["high"])
    medium_hits = _count_hits(text_l, URGENCY_KEYWORDS["medium"])
    exclaims = max(text.count("!") - 1, 0) * EXCLAIM_WEIGHT

    score = high_hits * 2 + medium_hits + exclaims

    # Days-since-order detection bumps urgency (e.g. "8 days ago")
    days_match = re.search(r"(\d+)\s*day", text_l)
    if days_match and int(days_match.group(1)) >= 5:
        score += 2

    if score >= 3:
        return "High"
    if score >= 1:
        return "Medium"
    return "Low"


def summarize(text: str, max_len: int = 140) -> str:
    """Cheap extractive summary: first sentence, trimmed, falls back to
    a truncated version of the whole complaint."""
    clean = re.sub(r"\s+", " ", text).strip()
    first_sentence = re.split(r"(?<=[.!?])\s", clean)[0]
    summary = first_sentence if len(first_sentence) > 15 else clean
    if len(summary) > max_len:
        summary = summary[: max_len - 1].rsplit(" ", 1)[0] + "…"
    return summary


def route_department(category: str) -> str:
    return DEPARTMENT_BY_CATEGORY.get(category, "Customer Support")


def generate_reply(customer_text: str, category: str, urgency: str) -> str:
    opener = {
        "High": "I'm really sorry for the trouble this has caused — I know this is frustrating, and I'm prioritizing it right now.",
        "Medium": "Thanks for flagging this, and sorry for the inconvenience.",
        "Low": "Thanks for reaching out!",
    }[urgency]

    body = {
        "Delivery": "I've escalated your shipment to our logistics team to get an updated tracking status and delivery estimate.",
        "Billing": "I've forwarded the transaction details to our finance team to review the charge and confirm next steps.",
        "Product Quality": "I've opened a case with our returns & warranty team so we can arrange an inspection, repair, or replacement.",
        "Account": "I've passed this to technical support to help verify your account and restore access.",
        "General Inquiry": "I've noted your question and someone from our team will follow up with the details you need.",
    }[category]

    closing = (
        "You'll hear back from us within a few hours given the urgency."
        if urgency == "High"
        else "You'll hear back from us within 1-2 business days."
    )

    return f"{opener} {body} {closing}"


def analyze_complaint(text: str, customer: str | None = None, order_id: str | None = None) -> dict:
    """Main entry point — Person 2 (Backend) calls exactly this function."""
    category = categorize(text)
    urgency = detect_urgency(text)
    return {
        "customer": customer or "Unknown",
        "order_id": order_id,
        "raw_text": text,
        "category": category,
        "urgency": urgency,
        "summary": summarize(text),
        "department": route_department(category),
        "suggested_action": SUGGESTED_ACTION.get(category, "Review and respond."),
        "reply": generate_reply(text, category, urgency),
        "analyzed_at": datetime.now(timezone.utc).isoformat(),
    }


# ---------------------------------------------------------------------------
# OPTIONAL: real LLM path. Same input/output shape as analyze_complaint().
# Requires: pip install anthropic, and ANTHROPIC_API_KEY set in the env.
# Swap this in inside app.py by changing one import line.
# ---------------------------------------------------------------------------

def analyze_with_llm(text: str, customer: str | None = None, order_id: str | None = None) -> dict:
    import json
    import anthropic

    client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from env

    prompt = f"""You are a customer support triage assistant. Given the complaint below,
respond with ONLY a JSON object (no markdown, no preamble) with exactly these keys:
category (one of: Delivery, Billing, Product Quality, Account, General Inquiry),
urgency (one of: Low, Medium, High),
summary (one sentence),
department (one of: Logistics, Finance, Returns & Warranty, Technical Support, Customer Support),
suggested_action (short phrase),
reply (a short, professional, empathetic reply to the customer).

Complaint: \"\"\"{text}\"\"\""""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}],
    )
    raw = "".join(block.text for block in response.content if block.type == "text")
    parsed = json.loads(raw.strip().strip("`").removeprefix("json").strip())

    return {
        "customer": customer or "Unknown",
        "order_id": order_id,
        "raw_text": text,
        **parsed,
        "analyzed_at": datetime.now(timezone.utc).isoformat(),
    }

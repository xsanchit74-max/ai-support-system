"""
sample_data.py — Person 4's work (Data & Testing)

A bank of realistic sample complaints covering every category/urgency
combination, so the team can seed the dashboard and demo the system
without waiting on real customer traffic. Also used by tests/test_ai_engine.py.
"""

SAMPLE_COMPLAINTS = [
    {
        "customer": "Rohan Mehta",
        "order_id": "ORD-10234",
        "text": "I ordered my laptop 8 days ago. It was supposed to arrive on Monday but the tracking hasn't changed for 4 days.",
    },
    {
        "customer": "Ananya Singh",
        "order_id": "ORD-10287",
        "text": "This is the WORST experience ever!! My package arrived completely SMASHED and the screen is cracked. I want a replacement immediately.",
    },
    {
        "customer": "Karan Bhatia",
        "order_id": "ORD-10301",
        "text": "I was charged twice for the same order. Can someone please look into this refund? A bit frustrated but not in a rush.",
    },
    {
        "customer": "Priya Nair",
        "order_id": None,
        "text": "Hi, just wondering how long the warranty on your headphones is. No rush, just curious!",
    },
    {
        "customer": "Vikram Chawla",
        "order_id": "ORD-10199",
        "text": "I can't log into my account, it says my password is wrong even after resetting it three times. Please help, I need to place an urgent order.",
    },
    {
        "customer": "Simran Kaur",
        "order_id": "ORD-10344",
        "text": "Still waiting on a response about my delayed shipment from last week. A bit disappointed with the silence so far.",
    },
    {
        "customer": "Arjun Verma",
        "order_id": "ORD-10410",
        "text": "This is unacceptable. I've emailed twice with no response and now I'm considering legal action over the overcharged amount on my card.",
    },
]

# Person 4 also owns these thresholds — tweak here, nowhere else in the app.
PRIORITY_RULES = {
    "High": "score >= 4 (multiple high-urgency keywords, angry tone, or 5+ days overdue)",
    "Medium": "score 2-3 (mild frustration, waiting, delayed)",
    "Low": "score 0-1 (neutral or informational tone)",
}

TEST_SCENARIOS = [
    ("Calm delivery question", "When will my order arrive? Just checking in.", "Delivery", "Low"),
    ("Angry billing complaint", "I was charged twice, this is fraud, I want a refund NOW!!", "Billing", "High"),
    ("Broken product, polite", "My headphones arrived broken, could you help me get a replacement?", "Product Quality", "Medium"),
    ("Locked out account", "I can't log in, password reset isn't working, please help urgently.", "Account", "High"),
]

"""
test_ai_engine.py — Person 4's work (Data & Testing)

Run with:
    cd ai-customer-support
    python -m pytest tests/ -v
(or just: python tests/test_ai_engine.py)
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

import ai_engine
from sample_data import TEST_SCENARIOS


def test_scenarios():
    passed, failed = 0, 0
    for name, text, expected_category, expected_urgency in TEST_SCENARIOS:
        result = ai_engine.analyze_complaint(text)
        ok_cat = result["category"] == expected_category
        ok_urg = result["urgency"] == expected_urgency
        status = "PASS" if (ok_cat and ok_urg) else "FAIL"
        if status == "PASS":
            passed += 1
        else:
            failed += 1
        print(f"[{status}] {name}")
        print(f"       expected category={expected_category!r} urgency={expected_urgency!r}")
        print(f"       got      category={result['category']!r} urgency={result['urgency']!r}")
    print(f"\n{passed} passed, {failed} failed out of {len(TEST_SCENARIOS)}")
    assert failed == 0


def test_original_example():
    """The exact example from the project brief."""
    text = "I ordered my laptop 8 days ago. It was supposed to arrive on Monday but the tracking hasn't changed for 4 days."
    result = ai_engine.analyze_complaint(text)
    assert result["category"] == "Delivery"
    assert result["urgency"] in ("Medium", "High")
    assert result["department"] == "Logistics"
    assert result["summary"]
    assert result["reply"]


if __name__ == "__main__":
    test_scenarios()
    test_original_example()
    print("\nAll checks complete.")

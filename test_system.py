"""
Automated validation and test suite for SmartSupport AI.
Covers the 6 required business test cases, SQLite CRUD operations,
hybrid rule evaluations, and fallback modes.
"""

import sys
import io

# Ensure UTF-8 output for Windows console
if sys.stdout.encoding != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
from database import (
    init_db,
    insert_ticket,
    get_all_tickets,
    get_ticket_by_id,
    update_ticket,
    get_dashboard_metrics,
    has_demo_data,
    insert_demo_tickets,
)
from ai_engine import analyze_ticket_with_gemini, rule_based_fallback_classifier
from ticket_manager import (
    generate_ticket_id,
    evaluate_hybrid_rules,
    get_demo_tickets,
)


def run_all_tests():
    print("=" * 60)
    print("SMARTSUPPORT AI - TEST SUITE")
    print("=" * 60)

    # 1. Initialize Database
    print("\n[TEST 1/5] Testing Database Initialization...")
    init_db()
    print("✓ SQLite database initialized successfully.")

    # 2. Test 6 Required Business Test Cases
    print("\n[TEST 2/5] Testing 6 Required Core Business Test Cases...")
    test_cases = [
        {
            "name": "TEST CASE 1 (Duplicate Charge)",
            "message": "I was charged twice for my monthly subscription.",
            "exp_category": "Billing Issue",
            "exp_priority": "High",
            "exp_team": "Billing Support",
        },
        {
            "name": "TEST CASE 2 (Application Crash)",
            "message": "The application crashes whenever I open it.",
            "exp_category": "Technical Issue",
            "exp_priority": "Medium",
            "exp_team": "Technical Support",
        },
        {
            "name": "TEST CASE 3 (Password Reset / How-to)",
            "message": "How can I change my account password?",
            "exp_category": "General Inquiry",
            "exp_priority": "Low",
            "exp_team": "Customer Service",
        },
        {
            "name": "TEST CASE 4 (Major Outage)",
            "message": "Your entire service is down and none of our employees can access it.",
            "exp_category": "Service Request",
            "exp_priority": "Critical",
            "exp_team": "Service Operations",
        },
        {
            "name": "TEST CASE 5 (Hardware Safety / Overheating)",
            "message": "My product is overheating and has started producing smoke.",
            "exp_category": "Product Defect",
            "exp_priority": "Critical",
            "exp_team": "Product Support",
        },
        {
            "name": "TEST CASE 6 (Delayed Refund)",
            "message": "My refund has not arrived.",
            "exp_category": "Billing Issue",
            "exp_priority": "Medium",
            "exp_team": "Billing Support",
        },
    ]

    all_passed = True
    for tc in test_cases:
        res = rule_based_fallback_classifier(tc["message"])
        cat_ok = res["category"] == tc["exp_category"]
        pri_ok = res["priority"] == tc["exp_priority"]
        team_ok = res["assigned_team"] == tc["exp_team"]

        status = "PASSED" if (cat_ok and pri_ok and team_ok) else "FAILED"
        print(f"  {tc['name']}: {status}")
        print(f"    Expected: {tc['exp_category']} | {tc['exp_priority']} | {tc['exp_team']}")
        print(f"    Got:      {res['category']} | {res['priority']} | {res['assigned_team']}")
        if not (cat_ok and pri_ok and team_ok):
            all_passed = False

    assert all_passed, "Some core business test cases failed!"
    print("✓ All 6 required business test cases passed perfectly.")

    # 3. Test Hybrid Rules Engine
    print("\n[TEST 3/5] Testing Hybrid Priority & Safety Rules...")
    safety_msg = "My product is overheating and has started producing smoke."
    safety_ai = {"priority": "Critical", "confidence": 95}
    warnings = evaluate_hybrid_rules(safety_msg, safety_ai)
    assert any("SAFETY HAZARD DETECTED" in w for w in warnings), "Safety hazard warning failed to trigger!"
    print(f"  Safety Warning triggered: {warnings[0][:65]}...")

    outage_msg = "Your entire service is down and none of our employees can access it."
    outage_ai = {"priority": "Critical", "confidence": 95}
    warnings2 = evaluate_hybrid_rules(outage_msg, outage_ai)
    assert any("MAJOR OUTAGE DETECTED" in w for w in warnings2), "Outage warning failed to trigger!"
    print(f"  Outage Warning triggered: {warnings2[0][:65]}...")
    print("✓ Hybrid rules verification passed.")

    # 4. Test Demo Dataset Loading & Duplication Prevention
    print("\n[TEST 4/5] Testing Demo Data Loading & Deduplication...")
    demo_count = insert_demo_tickets(get_demo_tickets())
    print(f"  Initial demo tickets inserted: {demo_count}")
    assert has_demo_data(), "Demo data check failed!"

    # Second load should insert 0 duplicates
    dupe_count = insert_demo_tickets(get_demo_tickets())
    print(f"  Second load attempt duplicates inserted: {dupe_count}")
    assert dupe_count == 0, f"Expected 0 duplicates, got {dupe_count}"
    print("✓ Demo dataset deduplication passed.")

    # 5. Test CRUD & Ticket Lifecycle
    print("\n[TEST 5/5] Testing Ticket CRUD Lifecycle...")
    test_id = generate_ticket_id()
    new_ticket = {
        "ticket_id": test_id,
        "customer_name": "QA Automator",
        "customer_email": "qa@testcorp.com",
        "source": "Email",
        "message": "Automated test message for ticket lifecycle validation.",
        "category": "Technical Issue",
        "priority": "Medium",
        "sentiment": "Neutral",
        "assigned_team": "Technical Support",
        "summary": "Automated verification ticket.",
        "recommended_action": "Verify database integrity.",
        "confidence": 90,
        "status": "Open",
    }
    inserted_id = insert_ticket(new_ticket)
    assert inserted_id == test_id, "Ticket ID mismatch!"

    fetched = get_ticket_by_id(test_id)
    assert fetched is not None, "Failed to retrieve ticket!"
    assert fetched["status"] == "Open"

    # Update status to In Progress
    update_ticket(test_id, {"status": "In Progress"})
    updated = get_ticket_by_id(test_id)
    assert updated["status"] == "In Progress", "Failed to update ticket status to In Progress"

    # Update status to Resolved
    update_ticket(test_id, {"status": "Resolved"})
    updated = get_ticket_by_id(test_id)
    assert updated["status"] == "Resolved", "Failed to update ticket status to Resolved"

    # Check metrics
    metrics = get_dashboard_metrics()
    print(f"  Total Tickets: {metrics['total']}, Open: {metrics['open']}, Resolved: {metrics['resolved']}")
    assert metrics["total"] >= 9, "Total ticket count mismatch!"
    print("✓ Ticket CRUD and metrics passed.")

    print("\n" + "=" * 60)
    print("ALL TESTS COMPLETED SUCCESSFULLY! READY FOR UI LAUNCH.")
    print("=" * 60)


if __name__ == "__main__":
    run_all_tests()

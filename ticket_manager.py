"""
Ticket Manager module for SmartSupport AI.
Coordinates hybrid business rules, safety checks, ticket validation, ID generation,
and demonstration dataset provisioning.
"""

import random
import string
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List
from database import get_ticket_by_id, insert_demo_tickets, has_demo_data


def generate_ticket_id() -> str:
    """
    Generates a unique, collision-free ticket ID in the format TICK-XXXX.
    """
    for _ in range(50):
        suffix = "".join(random.choices(string.digits, k=4))
        tid = f"TICK-{suffix}"
        if not get_ticket_by_id(tid):
            return tid
    # Fallback with timestamp component
    now_ms = int(datetime.now().timestamp() * 1000) % 100000
    return f"TICK-{now_ms}"


def evaluate_hybrid_rules(message: str, ai_result: Dict[str, Any]) -> List[str]:
    """
    Evaluates customer message against deterministic safety, outage, and policy rules.
    Returns a list of warnings or alerts for human review.
    Does NOT silently overwrite AI suggestions; surfaces alerts for human oversight.
    """
    warnings: List[str] = []
    msg_lower = message.lower()

    # Rule 1: Physical Safety Hazard Check
    safety_triggers = [
        "overheating", "overheat", "smoke", "fire", "burning", "burn",
        "exploded", "explosion", "sparking", "shock", "hazard", "injury"
    ]
    if any(k in msg_lower for k in safety_triggers):
        warnings.append(
            "⚠️ CRITICAL SAFETY HAZARD DETECTED: Customer reported smoke, overheating, or physical danger. "
            "Critical priority and immediate safety escalation protocol are strongly advised."
        )

    # Rule 2: Major Service Outage Check
    outage_triggers = [
        "entire service is down", "service is down", "system is down",
        "major outage", "all employees", "none of our employees", "global downtime"
    ]
    if any(k in msg_lower for k in outage_triggers):
        warnings.append(
            "🚨 MAJOR OUTAGE DETECTED: Widespread organizational or customer disruption reported. "
            "Escalation to Service Operations incident management is advised."
        )

    # Rule 3: AI Critical Priority Verification Requirement
    if ai_result.get("priority") == "Critical" and not warnings:
        warnings.append(
            "⚡ MANDATORY ESCALATION CHECK: AI classified this ticket as Critical. "
            "Please confirm impact severity before triggering high-priority on-call SLA."
        )

    # Rule 4: Low AI Confidence Warning
    confidence = ai_result.get("confidence", 100)
    if confidence < 75:
        warnings.append(
            f"ℹ️ LOW CONFIDENCE CLASSIFICATION ({confidence}%): AI model expressed uncertainty. "
            "Carefully review the proposed category and assigned department."
        )

    return warnings


def get_demo_tickets() -> List[Dict[str, Any]]:
    """
    Provides the 8 realistic customer tickets covering all core business scenarios.
    """
    now = datetime.now(timezone.utc)

    return [
        {
            "ticket_id": "TICK-1001",
            "customer_name": "Sarah Jenkins",
            "customer_email": "sarah.jenkins@acmecloud.com",
            "source": "Email",
            "message": "I was charged twice for my monthly subscription. Please look into this duplicate payment and issue a refund.",
            "category": "Billing Issue",
            "priority": "High",
            "sentiment": "Negative",
            "assigned_team": "Billing Support",
            "summary": "Customer reported being double-billed for their monthly subscription fee.",
            "recommended_action": "Verify duplicate payment transaction in billing portal and issue refund.",
            "confidence": 94,
            "status": "Open",
            "is_demo": 1,
            "created_at": (now - timedelta(hours=3)).strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": (now - timedelta(hours=3)).strftime("%Y-%m-%d %H:%M:%S"),
        },
        {
            "ticket_id": "TICK-1002",
            "customer_name": "David Miller",
            "customer_email": "dmiller@retaildirect.net",
            "source": "Chat",
            "message": "The package arrived today but the screen is cracked and the corner of the chassis is bent.",
            "category": "Product Defect",
            "priority": "Medium",
            "sentiment": "Negative",
            "assigned_team": "Product Support",
            "summary": "Customer received damaged product packaging with a cracked display and bent chassis.",
            "recommended_action": "Issue Return Merchandise Authorization (RMA) and arrange expedited replacement.",
            "confidence": 91,
            "status": "In Progress",
            "is_demo": 1,
            "created_at": (now - timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": (now - timedelta(hours=2)).strftime("%Y-%m-%d %H:%M:%S"),
        },
        {
            "ticket_id": "TICK-1003",
            "customer_name": "Elena Rostova",
            "customer_email": "elena.r@innovatix.org",
            "source": "Email",
            "message": "The application crashes whenever I open it and I am unable to log in to my account.",
            "category": "Technical Issue",
            "priority": "Medium",
            "sentiment": "Negative",
            "assigned_team": "Technical Support",
            "summary": "User reports desktop client crashes immediately upon launch, blocking account login.",
            "recommended_action": "Request crash dump log, verify user token auth, and advise cache clear.",
            "confidence": 89,
            "status": "Open",
            "is_demo": 1,
            "created_at": (now - timedelta(hours=14)).strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": (now - timedelta(hours=14)).strftime("%Y-%m-%d %H:%M:%S"),
        },
        {
            "ticket_id": "TICK-1004",
            "customer_name": "Marcus Sterling",
            "customer_email": "marcus.sterling@globexcorp.com",
            "source": "Chat",
            "message": "Your entire service is down and none of our employees can access it. Our entire team operations are halted.",
            "category": "Service Request",
            "priority": "Critical",
            "sentiment": "Negative",
            "assigned_team": "Service Operations",
            "summary": "Customer reports major enterprise-wide service outage impacting all staff members.",
            "recommended_action": "Page Tier-3 on-call incident commander and assess API cluster telemetry.",
            "confidence": 96,
            "status": "Open",
            "is_demo": 1,
            "created_at": (now - timedelta(minutes=45)).strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": (now - timedelta(minutes=45)).strftime("%Y-%m-%d %H:%M:%S"),
        },
        {
            "ticket_id": "TICK-1005",
            "customer_name": "Amanda Chen",
            "customer_email": "amanda.chen@solaris.io",
            "source": "Email",
            "message": "How can I change my account password and what are the export options for monthly reports?",
            "category": "General Inquiry",
            "priority": "Low",
            "sentiment": "Neutral",
            "assigned_team": "Customer Service",
            "summary": "Customer requests instructions for password reset and monthly report export formats.",
            "recommended_action": "Share knowledge base links for self-service security settings and report generation.",
            "confidence": 93,
            "status": "Resolved",
            "is_demo": 1,
            "created_at": (now - timedelta(days=2)).strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": (now - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S"),
        },
        {
            "ticket_id": "TICK-1006",
            "customer_name": "Robert Taylor",
            "customer_email": "rtaylor@fintechgroup.co",
            "source": "Chat",
            "message": "My refund has not arrived. It was approved two weeks ago by your billing representative.",
            "category": "Billing Issue",
            "priority": "Medium",
            "sentiment": "Negative",
            "assigned_team": "Billing Support",
            "summary": "Customer inquiring about status of a previously approved refund delayed beyond standard window.",
            "recommended_action": "Inspect merchant payout status with Stripe/Adyen and provide reference ARN to customer.",
            "confidence": 90,
            "status": "In Progress",
            "is_demo": 1,
            "created_at": (now - timedelta(days=1, hours=4)).strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": (now - timedelta(hours=5)).strftime("%Y-%m-%d %H:%M:%S"),
        },
        {
            "ticket_id": "TICK-1007",
            "customer_name": "Jonathan Reed",
            "customer_email": "jreed@summitlogistics.com",
            "source": "Email",
            "message": "My product is overheating and has started producing smoke. We had to disconnect power immediately.",
            "category": "Product Defect",
            "priority": "Critical",
            "sentiment": "Negative",
            "assigned_team": "Product Support",
            "summary": "Critical hardware safety risk: unit overheated and emitted smoke during normal operation.",
            "recommended_action": "Flag for product recall protocol, initiate immediate customer safety consultation.",
            "confidence": 98,
            "status": "Open",
            "is_demo": 1,
            "created_at": (now - timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": (now - timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S"),
        },
        {
            "ticket_id": "TICK-1008",
            "customer_name": "Sophie Dubois",
            "customer_email": "sophie.dubois@freemail.fr",
            "source": "Email",
            "message": "My order was supposed to arrive last Friday but tracking hasn't updated in 5 days. Can you check?",
            "category": "Service Request",
            "priority": "Medium",
            "sentiment": "Negative",
            "assigned_team": "Customer Service",
            "summary": "Customer tracking inquiry regarding shipment delay past the scheduled estimated delivery date.",
            "recommended_action": "Open freight inquiry with logistics partner and send updated tracking notice.",
            "confidence": 87,
            "status": "Resolved",
            "is_demo": 1,
            "created_at": (now - timedelta(days=3)).strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": (now - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S"),
        },
    ]


def load_demo_data_if_needed() -> int:
    """
    Loads demonstration tickets if the database is currently empty of demo data.
    """
    if not has_demo_data():
        return insert_demo_tickets(get_demo_tickets())
    return 0


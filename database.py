"""
Database management module for SmartSupport AI using SQLite.
Handles schema initialization, CRUD operations, filtering, and metric aggregations.
"""

import sqlite3
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from config import DB_PATH


def get_db_connection() -> sqlite3.Connection:
    """Creates a connection to the SQLite database with row factory."""
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Initializes the database schema if it doesn't already exist."""
    conn = get_db_connection()
    try:
        with conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS tickets (
                    ticket_id TEXT PRIMARY KEY,
                    customer_name TEXT NOT NULL,
                    customer_email TEXT,
                    source TEXT NOT NULL DEFAULT 'Email',
                    message TEXT NOT NULL,
                    category TEXT NOT NULL,
                    priority TEXT NOT NULL,
                    sentiment TEXT NOT NULL DEFAULT 'Neutral',
                    assigned_team TEXT NOT NULL,
                    summary TEXT NOT NULL,
                    recommended_action TEXT NOT NULL,
                    confidence INTEGER NOT NULL DEFAULT 85,
                    status TEXT NOT NULL DEFAULT 'Open',
                    is_demo INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            # Create indexes for fast querying on status, priority, category
            conn.execute("CREATE INDEX IF NOT EXISTS idx_status ON tickets(status)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_priority ON tickets(priority)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_category ON tickets(category)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_created_at ON tickets(created_at)")
    finally:
        conn.close()


def insert_ticket(ticket_data: Dict[str, Any]) -> str:
    """
    Inserts a newly approved ticket into the database.
    Returns the ticket_id.
    """
    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    conn = get_db_connection()
    try:
        with conn:
            conn.execute(
                """
                INSERT INTO tickets (
                    ticket_id, customer_name, customer_email, source,
                    message, category, priority, sentiment, assigned_team,
                    summary, recommended_action, confidence, status,
                    is_demo, created_at, updated_at
                ) VALUES (
                    :ticket_id, :customer_name, :customer_email, :source,
                    :message, :category, :priority, :sentiment, :assigned_team,
                    :summary, :recommended_action, :confidence, :status,
                    :is_demo, :created_at, :updated_at
                )
                """,
                {
                    "ticket_id": ticket_data["ticket_id"],
                    "customer_name": ticket_data["customer_name"],
                    "customer_email": ticket_data.get("customer_email", ""),
                    "source": ticket_data.get("source", "Email"),
                    "message": ticket_data["message"],
                    "category": ticket_data["category"],
                    "priority": ticket_data["priority"],
                    "sentiment": ticket_data.get("sentiment", "Neutral"),
                    "assigned_team": ticket_data["assigned_team"],
                    "summary": ticket_data["summary"],
                    "recommended_action": ticket_data["recommended_action"],
                    "confidence": int(ticket_data.get("confidence", 85)),
                    "status": ticket_data.get("status", "Open"),
                    "is_demo": 1 if ticket_data.get("is_demo") else 0,
                    "created_at": ticket_data.get("created_at", now_str),
                    "updated_at": ticket_data.get("updated_at", now_str),
                },
            )
        return ticket_data["ticket_id"]
    finally:
        conn.close()


def get_all_tickets(
    category: Optional[str] = None,
    priority: Optional[str] = None,
    status: Optional[str] = None,
    team: Optional[str] = None,
    search: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Retrieves tickets with optional filtering and search.
    Ordered by created_at DESC.
    """
    conn = get_db_connection()
    try:
        query = "SELECT * FROM tickets WHERE 1=1"
        params: List[Any] = []

        if category and category != "All":
            query += " AND category = ?"
            params.append(category)

        if priority and priority != "All":
            query += " AND priority = ?"
            params.append(priority)

        if status and status != "All":
            query += " AND status = ?"
            params.append(status)

        if team and team != "All":
            query += " AND assigned_team = ?"
            params.append(team)

        if search and search.strip():
            term = f"%{search.strip()}%"
            query += " AND (ticket_id LIKE ? OR customer_name LIKE ? OR message LIKE ? OR summary LIKE ?)"
            params.extend([term, term, term, term])

        query += " ORDER BY created_at DESC"
        cursor = conn.execute(query, params)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def get_ticket_by_id(ticket_id: str) -> Optional[Dict[str, Any]]:
    """Retrieves a single ticket by its ticket_id."""
    conn = get_db_connection()
    try:
        cursor = conn.execute("SELECT * FROM tickets WHERE ticket_id = ?", (ticket_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def update_ticket(ticket_id: str, updates: Dict[str, Any]) -> bool:
    """
    Updates designated fields of an existing ticket in SQLite.
    Automatically updates the `updated_at` timestamp.
    """
    allowed_fields = {
        "status",
        "priority",
        "assigned_team",
        "category",
        "summary",
        "recommended_action",
    }
    filtered_updates = {k: v for k, v in updates.items() if k in allowed_fields}
    if not filtered_updates:
        return False

    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    filtered_updates["updated_at"] = now_str

    set_clause = ", ".join([f"{k} = ?" for k in filtered_updates.keys()])
    params = list(filtered_updates.values())
    params.append(ticket_id)

    conn = get_db_connection()
    try:
        with conn:
            cursor = conn.execute(
                f"UPDATE tickets SET {set_clause} WHERE ticket_id = ?", params
            )
            return cursor.rowcount > 0
    finally:
        conn.close()


def delete_ticket(ticket_id: str) -> bool:
    """Deletes a ticket by ticket_id."""
    conn = get_db_connection()
    try:
        with conn:
            cursor = conn.execute("DELETE FROM tickets WHERE ticket_id = ?", (ticket_id,))
            return cursor.rowcount > 0
    finally:
        conn.close()


def has_demo_data() -> bool:
    """Checks if demo tickets already exist to prevent duplicate loading."""
    conn = get_db_connection()
    try:
        cursor = conn.execute("SELECT COUNT(*) as cnt FROM tickets WHERE is_demo = 1")
        row = cursor.fetchone()
        return (row["cnt"] if row else 0) > 0
    finally:
        conn.close()


def insert_demo_tickets(demo_tickets: List[Dict[str, Any]]) -> int:
    """
    Inserts a list of demonstration tickets.
    Returns the count of successfully inserted tickets.
    """
    count = 0
    for ticket in demo_tickets:
        # Check if already present by ticket_id
        if not get_ticket_by_id(ticket["ticket_id"]):
            insert_ticket(ticket)
            count += 1
    return count


def get_dashboard_metrics() -> Dict[str, Any]:
    """
    Computes key performance metrics and aggregation summaries directly from SQLite.
    Returns zeroed default values if the database is empty.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        # Total tickets
        cursor.execute("SELECT COUNT(*) as total FROM tickets")
        total = cursor.fetchone()["total"]

        if total == 0:
            return {
                "total": 0,
                "critical": 0,
                "high": 0,
                "open": 0,
                "in_progress": 0,
                "resolved": 0,
                "resolution_rate": 0.0,
            }

        # Priorities
        cursor.execute("SELECT COUNT(*) as cnt FROM tickets WHERE priority = 'Critical'")
        critical = cursor.fetchone()["cnt"]

        cursor.execute("SELECT COUNT(*) as cnt FROM tickets WHERE priority = 'High'")
        high = cursor.fetchone()["cnt"]

        # Statuses
        cursor.execute("SELECT COUNT(*) as cnt FROM tickets WHERE status = 'Open'")
        open_cnt = cursor.fetchone()["cnt"]

        cursor.execute("SELECT COUNT(*) as cnt FROM tickets WHERE status = 'In Progress'")
        in_progress_cnt = cursor.fetchone()["cnt"]

        cursor.execute("SELECT COUNT(*) as cnt FROM tickets WHERE status = 'Resolved'")
        resolved_cnt = cursor.fetchone()["cnt"]

        resolution_rate = round((resolved_cnt / total) * 100, 1) if total > 0 else 0.0

        return {
            "total": total,
            "critical": critical,
            "high": high,
            "open": open_cnt,
            "in_progress": in_progress_cnt,
            "resolved": resolved_cnt,
            "resolution_rate": resolution_rate,
        }
    finally:
        conn.close()


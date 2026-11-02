"""
Configuration and constants for SmartSupport AI.
NO streamlit imports here — config is a pure Python module.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file (local development)
load_dotenv()

# ── Directories ────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)
DB_PATH = DATA_DIR / "tickets.db"

# ── API Key (env-only; st.secrets is read in app.py) ───────
_PLACEHOLDERS = {
    "", "your_api_key_here", "your_actual_api_key_here",
    "paste_your_key_here", "your-api-key",
}

def _env_key() -> str:
    for var in ("GEMINI_API_KEY", "GOOGLE_API_KEY"):
        val = os.getenv(var, "").strip()
        if val and val.lower() not in _PLACEHOLDERS:
            return val
    return ""

GEMINI_API_KEY      = _env_key()
API_KEY_IS_SET      = bool(GEMINI_API_KEY)
DEFAULT_GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash").strip()

FALLBACK_MODEL_LIST = [
    "gemini-2.5-flash",
    "gemini-2.0-flash",
    "gemini-1.5-flash",
    "gemini-1.5-pro",
]

# ── Business Taxonomy ──────────────────────────────────────
CATEGORIES = [
    "General Inquiry",
    "Billing Issue",
    "Product Defect",
    "Technical Issue",
    "Service Request",
]

PRIORITIES = ["Critical", "High", "Medium", "Low"]

DEPARTMENTS = [
    "Customer Service",
    "Billing Support",
    "Product Support",
    "Technical Support",
    "Service Operations",
]

SENTIMENTS     = ["Positive", "Neutral", "Negative"]
TICKET_STATUSES = ["Open", "In Progress", "Resolved"]
REQUEST_SOURCES = ["Email", "Chat"]

# ── Colour Palette ─────────────────────────────────────────
PRIORITY_COLORS = {
    "Critical": "#DC2626",
    "High":     "#EA580C",
    "Medium":   "#D97706",
    "Low":      "#16A34A",
}

PRIORITY_BG_COLORS = {
    "Critical": "#FEE2E2",
    "High":     "#FFEDD5",
    "Medium":   "#FEF3C7",
    "Low":      "#DCFCE7",
}

STATUS_COLORS = {
    "Open":        "#2563EB",
    "In Progress": "#D97706",
    "Resolved":    "#16A34A",
}

SENTIMENT_COLORS = {
    "Positive": "#16A34A",
    "Neutral":  "#64748B",
    "Negative": "#DC2626",
}

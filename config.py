"""
Configuration and constants for SmartSupport AI.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()

# Base directories
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)
DB_PATH = DATA_DIR / "tickets.db"

# ---------------------------------------------------------------------------
# API KEY LOADING — 3-layer priority:
#   1. Streamlit Cloud st.secrets (production cloud deployment)
#   2. .env file / OS environment variable (local development)
#   3. Empty → rule-based fallback activates automatically
# ---------------------------------------------------------------------------
_PLACEHOLDER_STRINGS = {
    "your_api_key_here",
    "your_actual_api_key_here",
    "paste_your_key_here",
    "your-api-key",
    "",
}

def _load_api_key() -> str:
    """Loads Gemini API key from Streamlit secrets or environment variables."""
    # Priority 1: Streamlit Cloud st.secrets
    try:
        import streamlit as st
        key = st.secrets.get("GEMINI_API_KEY", "").strip()
        if key and key.lower() not in _PLACEHOLDER_STRINGS:
            return key
    except Exception:
        pass

    # Priority 2: .env file / OS environment variable
    key = os.getenv("GEMINI_API_KEY", "").strip()
    if key and key.lower() not in _PLACEHOLDER_STRINGS:
        return key

    # Priority 3: Legacy alias
    key = os.getenv("GOOGLE_API_KEY", "").strip()
    if key and key.lower() not in _PLACEHOLDER_STRINGS:
        return key

    return ""


def _load_model() -> str:
    try:
        import streamlit as st
        m = st.secrets.get("GEMINI_MODEL", "").strip()
        if m:
            return m
    except Exception:
        pass
    return os.getenv("GEMINI_MODEL", "gemini-2.5-flash").strip()


GEMINI_API_KEY = _load_api_key()
API_KEY_IS_SET = bool(GEMINI_API_KEY)
DEFAULT_GEMINI_MODEL = _load_model()
FALLBACK_MODEL_LIST = [
    "gemini-2.5-flash",
    "gemini-2.0-flash",
    "gemini-1.5-flash",
    "gemini-1.5-pro",
]

# Business Taxonomy - Categories
CATEGORIES = [
    "General Inquiry",
    "Billing Issue",
    "Product Defect",
    "Technical Issue",
    "Service Request",
]

# Business Taxonomy - Priorities
PRIORITIES = [
    "Critical",
    "High",
    "Medium",
    "Low",
]

# Business Taxonomy - Departments
DEPARTMENTS = [
    "Customer Service",
    "Billing Support",
    "Product Support",
    "Technical Support",
    "Service Operations",
]

# Sentiments
SENTIMENTS = [
    "Positive",
    "Neutral",
    "Negative",
]

# Ticket Statuses
TICKET_STATUSES = [
    "Open",
    "In Progress",
    "Resolved",
]

# Sources
REQUEST_SOURCES = [
    "Email",
    "Chat",
]

# Color Palette for SaaS UI
PRIORITY_COLORS = {
    "Critical": "#DC2626",  # Red
    "High": "#EA580C",      # Orange
    "Medium": "#D97706",    # Amber/Yellow
    "Low": "#16A34A",       # Green
}

PRIORITY_BG_COLORS = {
    "Critical": "#FEE2E2",
    "High": "#FFEDD5",
    "Medium": "#FEF3C7",
    "Low": "#DCFCE7",
}

STATUS_COLORS = {
    "Open": "#2563EB",        # Blue
    "In Progress": "#D97706", # Amber
    "Resolved": "#16A34A",    # Green
}

SENTIMENT_COLORS = {
    "Positive": "#16A34A",
    "Neutral": "#64748B",
    "Negative": "#DC2626",
}


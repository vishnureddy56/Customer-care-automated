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

# API Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or ""
DEFAULT_GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
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


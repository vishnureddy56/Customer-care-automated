# SmartSupport AI: AI-Powered Customer Support Ticket Triage System

> **Tagline:** Intelligent Customer Support. Faster Decisions. Better Service.

**SmartSupport AI** is a full-stack, AI-powered customer support ticket triage prototype designed to eliminate manual reading delays, prevent misrouting, instantly detect safety hazards, and prioritize critical outages with human-in-the-loop oversight.

---

## 🌟 Key Business Value & Features

1. **Intelligent Inbound Triage:** Automatically analyzes incoming email and chat requests to determine issue category, business priority, customer sentiment, concise issue summary, and department routing.
2. **Hybrid Priority & Safety Rules Engine:** Business-rule guardrails that intercept safety hazards (fire, smoke, overheating) and major outages, enforcing mandatory human review before escalation.
3. **Human Review & Approval Gate:** AI acts as a recommendation copilot. Human agents review, adjust, and approve classifications before tickets are committed to the database.
4. **Persistent SQLite Ticket Management:** Filter, search, inspect, and update ticket lifecycle states (`Open` → `In Progress` → `Resolved`).
5. **Real-Time Operational Dashboard:** Interactive Plotly metric cards and distributions (Category, Priority, Department workload, and Status).
6. **Data-Grounded AI Insights:** Real-time business intelligence calculated from stored tickets, providing dynamic staffing and operational alerts without hallucinations.
7. **Transparent Fallback Mode:** Operates reliably even without an active internet connection or Gemini API key, using a clearly labeled deterministic heuristic engine.

---

## 🏗️ Architecture & Folder Structure

```
SmartSupport-AI/
│
├── app.py                  # Main Streamlit web application & navigation
├── ai_engine.py            # Gemini integration, JSON prompt schema & fallback classifier
├── ticket_manager.py       # Hybrid business rules, safety checks & demo dataset
├── database.py             # SQLite database layer, schema, indexes & CRUD operations
├── config.py               # Taxonomies, color palettes, models & environment settings
├── test_system.py          # Automated verification suite for the 6 core business cases
├── requirements.txt        # Python dependency declarations
├── .env.example            # Template for environment configuration
├── .gitignore              # Files to exclude from source control
├── README.md               # Architecture documentation & operating manual
│
└── data/
    └── tickets.db          # SQLite persistent database (created automatically)
```

---

## 🛠️ Technology Stack

- **Frontend & Web Server:** [Streamlit](https://streamlit.io/) (Python)
- **AI & LLM Services:** [Google Gemini API](https://aistudio.google.com/) (`gemini-2.5-flash`, `gemini-2.0-flash`, `gemini-1.5-flash`) with structured JSON schema
- **Data Persistence:** [SQLite](https://www.sqlite.org/) with parameterized SQL queries and indexes
- **Data Analytics:** [Pandas](https://pandas.pydata.org/)
- **Visualizations:** [Plotly](https://plotly.com/python/)

---

## 🚀 Quick Start Guide

### 1. Prerequisites
- Python 3.10+ (Tested on Python 3.14)
- Git (optional)

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. (Optional) Configure Gemini API Key
To use live Google Gemini AI, copy `.env.example` to `.env` or set the environment variable:

```bash
# In .env or shell environment
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-flash
```

> **Note:** An API key is **not required** to test or demonstrate SmartSupport AI. If omitted, the system seamlessly activates the transparent **"Rule-based fallback mode – AI service unavailable"** engine. You can also input or change your API key live directly in the application sidebar!

### 4. Run the Automated Tests
Verify all 6 core business scenarios, database operations, and hybrid safety rules:
```bash
python test_system.py
```

### 5. Launch the Application
```bash
python -m streamlit run app.py
# or
streamlit run app.py
```
Open your browser to `http://localhost:8501`.

---

## 🧪 Demonstration Walkthrough

Follow this step-by-step workflow during a live demo:

1. **Open Dashboard:** Observe the KPI metric cards and Plotly charts. If the database is empty, click **"🚀 Load 8 Realistic Demo Tickets Now"** or use the sidebar **"Load Demo"** button.
2. **Navigate to "➕ Create New Ticket":**
   - Click one of the quick test buttons (e.g., **"Overheating Hazard"** or **"Duplicate Charge"**).
   - Click **"🤖 Analyze with AI"**.
   - Review the AI diagnostic results (Category, Priority, Sentiment, Summary, Action, and Confidence).
   - Observe the **Hybrid Safety Warning** if safety hazard keywords (smoke, fire, overheat) are present.
3. **Human Approval:**
   - Modify the priority or assigned team if desired.
   - Click **"✅ Approve and Create Ticket"**.
   - Receive the unique ticket ID (e.g. `TICK-8314`).
4. **Manage Tickets:**
   - Navigate to **"📋 Manage Tickets"**.
   - Filter by status (`Open`), priority (`Critical`), or search by customer name.
   - Select the newly created ticket, change its status to `In Progress` or `Resolved`, and click **"💾 Save Changes"**.
5. **Inspect AI Insights:**
   - Navigate to **"💡 AI Insights"** to review the data-grounded observations and operational workload distribution.

---

## 📋 Core Test Scenarios Verified

| # | Customer Input Message | Expected Category | Expected Priority | Responsible Team | Test Result |
|---|------------------------|-------------------|-------------------|------------------|-------------|
| 1 | "I was charged twice for my monthly subscription." | Billing Issue | High | Billing Support | ✅ PASSED |
| 2 | "The application crashes whenever I open it." | Technical Issue | Medium | Technical Support | ✅ PASSED |
| 3 | "How can I change my account password?" | General Inquiry | Low | Customer Service | ✅ PASSED |
| 4 | "Your entire service is down and none of our employees can access it." | Service Request | Critical | Service Operations | ✅ PASSED |
| 5 | "My product is overheating and has started producing smoke." | Product Defect | Critical | Product Support | ✅ PASSED |
| 6 | "My refund has not arrived." | Billing Issue | Medium | Billing Support | ✅ PASSED |

---

## 🔒 Security & Responsible AI Considerations

- **Prompt Injection Defense:** Customer inputs are treated exclusively as untrusted data within system instruction boundaries.
- **Human-in-the-Loop Oversight:** AI recommendations never finalize a ticket without human agent approval.
- **Privacy First:** Data persists locally in SQLite; sensitive credentials are never written to application logs or client repositories.
- **Transparent Attribution:** Results clearly distinguish between live Gemini model outputs and heuristic fallback classifications.

---

## ⚠️ Known Prototype Limitations

- Email server (IMAP/SMTP) polling and live webhook ingest are omitted for the prototype scope.
- Multi-user concurrent agent locking on individual tickets is not implemented.
- Offline rule-based fallback utilizes fixed keyword heuristics rather than a local quantized embedding model.

"""
SmartSupport AI - Streamlit Application
AI-Powered Customer Support Ticket Triage System
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timezone

from config import (
    CATEGORIES,
    PRIORITIES,
    DEPARTMENTS,
    SENTIMENTS,
    TICKET_STATUSES,
    REQUEST_SOURCES,
    PRIORITY_COLORS,
    STATUS_COLORS,
    SENTIMENT_COLORS,
    GEMINI_API_KEY,
    API_KEY_IS_SET,
    DEFAULT_GEMINI_MODEL,
    FALLBACK_MODEL_LIST,
)
from database import (
    init_db,
    insert_ticket,
    get_all_tickets,
    get_ticket_by_id,
    update_ticket,
    delete_ticket,
    get_dashboard_metrics,
    has_demo_data,
    insert_demo_tickets,
)
from ai_engine import analyze_ticket_with_gemini
from ticket_manager import (
    generate_ticket_id,
    evaluate_hybrid_rules,
    get_demo_tickets,
)

# Page Configuration
st.set_page_config(
    page_title="SmartSupport AI - Ticket Triage",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize database schema automatically
init_db()

# Custom SaaS UI Styling
st.markdown(
    """
    <style>
    /* Global Styles */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* SaaS Card Styles */
    .metric-card {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 16px 20px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
        transition: transform 0.15s ease-in-out, box-shadow 0.15s ease-in-out;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .metric-title {
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #64748B;
        margin-bottom: 6px;
    }
    .metric-value {
        font-size: 1.85rem;
        font-weight: 700;
        color: #0F172A;
    }
    .metric-subtext {
        font-size: 0.75rem;
        color: #94A3B8;
        margin-top: 4px;
    }
    
    /* Badges */
    .badge {
        display: inline-block;
        padding: 3px 8px;
        font-size: 0.75rem;
        font-weight: 600;
        border-radius: 6px;
        text-align: center;
    }
    .badge-critical { background-color: #FEE2E2; color: #991B1B; border: 1px solid #FCA5A5; }
    .badge-high { background-color: #FFEDD5; color: #9A3412; border: 1px solid #FDBA74; }
    .badge-medium { background-color: #FEF3C7; color: #92400E; border: 1px solid #FCD34D; }
    .badge-low { background-color: #DCFCE7; color: #166534; border: 1px solid #86EFAC; }
    
    .badge-open { background-color: #DBEAFE; color: #1E40AF; border: 1px solid #93C5FD; }
    .badge-inprogress { background-color: #FEF3C7; color: #92400E; border: 1px solid #FCD34D; }
    .badge-resolved { background-color: #DCFCE7; color: #166534; border: 1px solid #86EFAC; }

    /* Callouts & Section Headers */
    .section-header {
        font-size: 1.25rem;
        font-weight: 700;
        color: #0F172A;
        margin-top: 10px;
        margin-bottom: 15px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .review-box {
        background: #F8FAFC;
        border: 1px solid #CBD5E1;
        border-radius: 12px;
        padding: 20px;
        margin-top: 16px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# Helper: Badge HTML renderer
def render_priority_badge(priority: str) -> str:
    css_class = f"badge-{priority.lower()}"
    return f'<span class="badge {css_class}">{priority}</span>'


def render_status_badge(status: str) -> str:
    clean = status.lower().replace(" ", "")
    return f'<span class="badge badge-{clean}">{status}</span>'


# ==============================================================================
# SIDEBAR
# ==============================================================================
with st.sidebar:
    st.markdown("### 🛡️ SmartSupport AI")
    st.markdown(
        "<div style='font-size: 0.8rem; color: #64748B; margin-top: -10px; margin-bottom: 15px;'>"
        "Intelligent Customer Support. Faster Decisions. Better Service.</div>",
        unsafe_allow_html=True,
    )

    st.markdown("---")

    nav_selection = st.radio(
        "Navigation",
        [
            "📊 Overview Dashboard",
            "➕ Create New Ticket",
            "📋 Manage Tickets",
            "💡 AI Insights",
        ],
        index=0,
    )

    st.markdown("---")
    st.markdown("#### ⚙️ AI Engine Settings")

    # API Key Handling
    custom_api_key = st.text_input(
        "Gemini API Key",
        value=GEMINI_API_KEY,
        type="password",
        help="Paste your key from https://aistudio.google.com/app/apikey — or add it to the .env file.",
        placeholder="AIza...",
    )

    active_api_key = custom_api_key.strip() if custom_api_key else GEMINI_API_KEY

    selected_model = st.selectbox(
        "Model Selection",
        options=FALLBACK_MODEL_LIST,
        index=0,
        help="Configurable Gemini model for JSON triage analysis.",
    )

    # API Connection Indicator
    if active_api_key:
        st.success("🟢 Gemini API Key Active")
    else:
        st.warning("🟡 No API Key — Fallback Mode Active")
        st.caption(
            "Add your free key at [aistudio.google.com](https://aistudio.google.com/app/apikey) "
            "then paste it above **or** add it to your `.env` file."
        )

    st.markdown("---")
    st.markdown("#### 🧪 Demo Data Controls")
    
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        if st.button("Load Demo", use_container_width=True, help="Populate 8 realistic business support tickets"):
            inserted = insert_demo_tickets(get_demo_tickets())
            if inserted > 0:
                st.success(f"Loaded {inserted} tickets!")
                st.rerun()
            else:
                st.info("Demo tickets already loaded.")

    with col_d2:
        if st.button("Clear Demo", use_container_width=True, help="Remove demo tickets"):
            all_demo = get_all_tickets()
            deleted = 0
            for t in all_demo:
                if t.get("is_demo") == 1:
                    delete_ticket(t["ticket_id"])
                    deleted += 1
            st.warning(f"Cleared {deleted} tickets.")
            st.rerun()


# ==============================================================================
# SECTION 1: OVERVIEW DASHBOARD
# ==============================================================================
if nav_selection == "📊 Overview Dashboard":
    st.markdown("<div class='section-header'>📊 Support Operations Overview</div>", unsafe_allow_html=True)
    st.caption("Real-time operational metrics and ticket distributions across departments.")

    metrics = get_dashboard_metrics()
    tickets_list = get_all_tickets()

    # Metric Cards (5 Cards)
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-title">Total Tickets</div>
                <div class="metric-value">{metrics['total']}</div>
                <div class="metric-subtext">All time requests</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            f"""
            <div class="metric-card" style="border-left: 4px solid #DC2626;">
                <div class="metric-title" style="color: #991B1B;">Critical Priority</div>
                <div class="metric-value" style="color: #DC2626;">{metrics['critical']}</div>
                <div class="metric-subtext">Immediate action</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            f"""
            <div class="metric-card" style="border-left: 4px solid #EA580C;">
                <div class="metric-title" style="color: #9A3412;">High Priority</div>
                <div class="metric-value" style="color: #EA580C;">{metrics['high']}</div>
                <div class="metric-subtext">Elevated urgency</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c4:
        st.markdown(
            f"""
            <div class="metric-card" style="border-left: 4px solid #2563EB;">
                <div class="metric-title" style="color: #1E40AF;">Open Queue</div>
                <div class="metric-value" style="color: #2563EB;">{metrics['open']}</div>
                <div class="metric-subtext">Awaiting triage/work</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c5:
        st.markdown(
            f"""
            <div class="metric-card" style="border-left: 4px solid #16A34A;">
                <div class="metric-title" style="color: #166534;">Resolved</div>
                <div class="metric-value" style="color: #16A34A;">{metrics['resolved']}</div>
                <div class="metric-subtext">{metrics['resolution_rate']}% resolution rate</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # Empty State check
    if metrics["total"] == 0:
        st.info("ℹ️ No tickets currently exist in the database. You can manually create a ticket or load demo tickets.")
        if st.button("🚀 Load 8 Realistic Demo Tickets Now"):
            insert_demo_tickets(get_demo_tickets())
            st.rerun()
    else:
        # Convert to Pandas for Plotly Visualizations
        df = pd.DataFrame(tickets_list)

        chart_row1_col1, chart_row1_col2 = st.columns(2)
        
        # Chart A: Tickets by Category
        with chart_row1_col1:
            cat_counts = df["category"].value_counts().reset_index()
            cat_counts.columns = ["Category", "Count"]
            fig_cat = px.pie(
                cat_counts,
                values="Count",
                names="Category",
                hole=0.55,
                title="Tickets by Category",
                color_discrete_sequence=px.colors.qualitative.Pastel,
            )
            fig_cat.update_layout(
                margin=dict(l=20, r=20, t=40, b=20),
                legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5),
            )
            st.plotly_chart(fig_cat, use_container_width=True)

        # Chart B: Tickets by Priority
        with chart_row1_col2:
            priority_order = ["Critical", "High", "Medium", "Low"]
            pri_counts = (
                df["priority"]
                .value_counts()
                .reindex(priority_order, fill_value=0)
                .reset_index()
            )
            pri_counts.columns = ["Priority", "Count"]

            bar_colors = [PRIORITY_COLORS.get(p, "#94A3B8") for p in pri_counts["Priority"]]
            fig_pri = px.bar(
                pri_counts,
                x="Priority",
                y="Count",
                title="Tickets by Priority Level",
                color="Priority",
                color_discrete_map=PRIORITY_COLORS,
                text="Count",
            )
            fig_pri.update_layout(
                showlegend=False,
                margin=dict(l=20, r=20, t=40, b=20),
                xaxis_title="",
                yaxis_title="Tickets",
            )
            fig_pri.update_traces(textposition="outside")
            st.plotly_chart(fig_pri, use_container_width=True)

        chart_row2_col1, chart_row2_col2 = st.columns(2)

        # Chart C: Tickets by Department
        with chart_row2_col1:
            dept_counts = df["assigned_team"].value_counts().reset_index()
            dept_counts.columns = ["Department", "Count"]
            fig_dept = px.bar(
                dept_counts,
                x="Count",
                y="Department",
                orientation="h",
                title="Workload by Assigned Department",
                color_discrete_sequence=["#3B82F6"],
                text="Count",
            )
            fig_dept.update_layout(
                margin=dict(l=20, r=20, t=40, b=20),
                yaxis=dict(autorange="reversed"),
                xaxis_title="Tickets",
                yaxis_title="",
            )
            fig_dept.update_traces(textposition="outside")
            st.plotly_chart(fig_dept, use_container_width=True)

        # Chart D: Ticket Status Distribution
        with chart_row2_col2:
            status_counts = df["status"].value_counts().reset_index()
            status_counts.columns = ["Status", "Count"]
            fig_status = px.pie(
                status_counts,
                values="Count",
                names="Status",
                hole=0.55,
                title="Ticket Status Distribution",
                color="Status",
                color_discrete_map=STATUS_COLORS,
            )
            fig_status.update_layout(
                margin=dict(l=20, r=20, t=40, b=20),
                legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5),
            )
            st.plotly_chart(fig_status, use_container_width=True)

        # Recent Tickets Table
        st.markdown("<div class='section-header'>🕒 Recent Customer Tickets</div>", unsafe_allow_html=True)
        recent_df = df.head(8)[
            [
                "ticket_id",
                "customer_name",
                "source",
                "category",
                "priority",
                "assigned_team",
                "status",
                "created_at",
            ]
        ].copy()
        recent_df.columns = [
            "Ticket ID",
            "Customer",
            "Source",
            "Category",
            "Priority",
            "Assigned Team",
            "Status",
            "Created Date",
        ]

        st.dataframe(
            recent_df,
            use_container_width=True,
            hide_index=True,
        )


# ==============================================================================
# SECTION 2: CREATE NEW TICKET (AI TRIAGE & HUMAN APPROVAL)
# ==============================================================================
elif nav_selection == "➕ Create New Ticket":
    st.markdown("<div class='section-header'>➕ Create & Triage New Ticket</div>", unsafe_allow_html=True)
    st.caption("Input customer requests to receive automated AI classification, priority detection, and team routing.")

    # State initialization for current triage review
    if "triage_result" not in st.session_state:
        st.session_state.triage_result = None
    if "current_input_data" not in st.session_state:
        st.session_state.current_input_data = {}

    # Quick Template Buttons for Fast Demonstration
    st.markdown("##### ⚡ Quick Demonstration Templates")
    demo_cols = st.columns(6)
    template_data = {
        "Duplicate Charge": {
            "name": "Sarah Jenkins",
            "email": "sarah.j@example.com",
            "source": "Email",
            "message": "I was charged twice for my monthly subscription.",
        },
        "App Crash": {
            "name": "Alex Mercer",
            "email": "alex.m@example.com",
            "source": "Chat",
            "message": "The application crashes whenever I open it.",
        },
        "Password Reset": {
            "name": "Jordan Lee",
            "email": "jordan.l@example.com",
            "source": "Email",
            "message": "How can I change my account password?",
        },
        "Major Outage": {
            "name": "Enterprise IT Admin",
            "email": "it-ops@globalcorp.com",
            "source": "Chat",
            "message": "Your entire service is down and none of our employees can access it.",
        },
        "Overheating Hazard": {
            "name": "Jonathan Reed",
            "email": "jreed@summit.org",
            "source": "Email",
            "message": "My product is overheating and has started producing smoke.",
        },
        "Delayed Refund": {
            "name": "Robert Taylor",
            "email": "rtaylor@fintech.co",
            "source": "Chat",
            "message": "My refund has not arrived.",
        },
    }

    selected_template = None
    for idx, (label, data) in enumerate(template_data.items()):
        with demo_cols[idx]:
            if st.button(label, use_container_width=True):
                st.session_state["form_name"] = data["name"]
                st.session_state["form_email"] = data["email"]
                st.session_state["form_source"] = data["source"]
                st.session_state["form_message"] = data["message"]
                st.session_state.triage_result = None

    # Input Form
    with st.form("new_ticket_form"):
        col_c1, col_c2, col_c3 = st.columns([2, 2, 1])
        with col_c1:
            customer_name = st.text_input(
                "Customer Name *",
                value=st.session_state.get("form_name", "Sarah Jenkins"),
                placeholder="e.g. Jane Doe",
            )
        with col_c2:
            customer_email = st.text_input(
                "Customer Email (Optional)",
                value=st.session_state.get("form_email", "sarah.j@example.com"),
                placeholder="customer@domain.com",
            )
        with col_c3:
            default_source_idx = (
                0 if st.session_state.get("form_source", "Email") == "Email" else 1
            )
            request_source = st.selectbox(
                "Request Source",
                options=REQUEST_SOURCES,
                index=default_source_idx,
            )

        customer_message = st.text_area(
            "Customer Message *",
            value=st.session_state.get(
                "form_message",
                "I was charged twice for my monthly subscription.",
            ),
            height=120,
            placeholder="Paste customer support inquiry, error log, or chat transcript...",
        )

        analyze_submitted = st.form_submit_button("🤖 Analyze with AI", use_container_width=True, type="primary")

    if analyze_submitted:
        if not customer_message.strip():
            st.error("Please enter a customer message before analyzing.")
        else:
            with st.spinner("Analyzing customer message and evaluating business rules..."):
                triage_res = analyze_ticket_with_gemini(
                    message=customer_message,
                    api_key=active_api_key,
                    model_name=selected_model,
                )
                rule_warnings = evaluate_hybrid_rules(customer_message, triage_res)
                triage_res["rule_warnings"] = rule_warnings

                # Store in session state for review form
                st.session_state.triage_result = triage_res
                st.session_state.current_input_data = {
                    "customer_name": customer_name,
                    "customer_email": customer_email,
                    "source": request_source,
                    "message": customer_message,
                }

    # ==============================================================================
    # HUMAN REVIEW AND APPROVAL CARD (FEATURE 4 & HYBRID RULES)
    # ==============================================================================
    if st.session_state.triage_result:
        triage = st.session_state.triage_result
        input_data = st.session_state.current_input_data

        st.markdown("<hr style='margin: 25px 0;'>", unsafe_allow_html=True)
        st.markdown("<div class='section-header'>🕵️ Human Review & Approval Gate</div>", unsafe_allow_html=True)
        st.caption("AI-assisted recommendation. Human support agents retain full control to adjust categories and priority.")

        # Status mode label
        if triage.get("is_fallback"):
            st.warning(
                f"⚠️ **{triage.get('mode_label', 'Rule-based fallback mode – AI service unavailable.')}**\n\n"
                f"*Reason: {triage.get('fallback_reason', 'External API inactive.')}*"
            )
        else:
            st.success(f"🟢 **{triage.get('mode_label', 'Analyzed via Gemini AI')}**")

        # Hybrid Rule Warnings
        if triage.get("rule_warnings"):
            for w in triage["rule_warnings"]:
                st.error(w)

        # Review & Edit Container
        with st.container():
            col_rev1, col_rev2 = st.columns([1, 1])

            with col_rev1:
                st.markdown("##### 📄 Original Customer Context")
                st.markdown(f"**Customer:** {input_data.get('customer_name')} ({input_data.get('source')})")
                if input_data.get("customer_email"):
                    st.markdown(f"**Email:** {input_data.get('customer_email')}")
                st.text_area("Customer Message", value=input_data.get("message"), height=90, disabled=True)

                st.markdown("##### 🔍 AI Diagnostic Telemetry")
                col_m1, col_m2 = st.columns(2)
                with col_m1:
                    st.metric("Sentiment", triage.get("sentiment", "Neutral"))
                with col_m2:
                    conf = triage.get("confidence", 85)
                    st.metric("AI Confidence", f"{conf}%")

            with col_rev2:
                st.markdown("##### ✏️ Agent Decision & Adjustments")

                cat_idx = (
                    CATEGORIES.index(triage.get("category"))
                    if triage.get("category") in CATEGORIES
                    else 0
                )
                approved_category = st.selectbox("Category", options=CATEGORIES, index=cat_idx)

                pri_idx = (
                    PRIORITIES.index(triage.get("priority"))
                    if triage.get("priority") in PRIORITIES
                    else 2
                )
                approved_priority = st.selectbox("Priority", options=PRIORITIES, index=pri_idx)

                dept_idx = (
                    DEPARTMENTS.index(triage.get("assigned_team"))
                    if triage.get("assigned_team") in DEPARTMENTS
                    else 0
                )
                approved_team = st.selectbox("Assigned Department", options=DEPARTMENTS, index=dept_idx)

                approved_summary = st.text_input("Concise Issue Summary", value=triage.get("summary", ""))
                approved_action = st.text_input("Recommended Action", value=triage.get("recommended_action", ""))

            # Final Decision Actions
            st.markdown("<br>", unsafe_allow_html=True)
            col_act1, col_act2 = st.columns([3, 1])

            with col_act1:
                if st.button("✅ Approve and Create Ticket", type="primary", use_container_width=True):
                    new_id = generate_ticket_id()
                    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

                    ticket_record = {
                        "ticket_id": new_id,
                        "customer_name": input_data["customer_name"],
                        "customer_email": input_data.get("customer_email", ""),
                        "source": input_data.get("source", "Email"),
                        "message": input_data["message"],
                        "category": approved_category,
                        "priority": approved_priority,
                        "sentiment": triage.get("sentiment", "Neutral"),
                        "assigned_team": approved_team,
                        "summary": approved_summary,
                        "recommended_action": approved_action,
                        "confidence": triage.get("confidence", 85),
                        "status": "Open",
                        "is_demo": 0,
                        "created_at": now_str,
                        "updated_at": now_str,
                    }

                    insert_ticket(ticket_record)
                    st.success(f"🎉 Ticket **{new_id}** created and assigned to **{approved_team}**!")
                    st.balloons()
                    # Reset state
                    st.session_state.triage_result = None
                    st.session_state.current_input_data = {}

            with col_act2:
                if st.button("❌ Discard", use_container_width=True):
                    st.session_state.triage_result = None
                    st.session_state.current_input_data = {}
                    st.info("Triage draft discarded.")
                    st.rerun()


# ==============================================================================
# SECTION 3: MANAGE TICKETS
# ==============================================================================
elif nav_selection == "📋 Manage Tickets":
    st.markdown("<div class='section-header'>📋 Support Ticket Management</div>", unsafe_allow_html=True)
    st.caption("Search, filter, inspect, and update customer tickets stored in SQLite.")

    # Filter Bar
    filter_col1, filter_col2, filter_col3, filter_col4, filter_col5 = st.columns(5)
    with filter_col1:
        search_query = st.text_input("🔍 Search", placeholder="Ticket ID, name, keyword...")
    with filter_col2:
        status_filter = st.selectbox("Status", ["All"] + TICKET_STATUSES)
    with filter_col3:
        priority_filter = st.selectbox("Priority", ["All"] + PRIORITIES)
    with filter_col4:
        category_filter = st.selectbox("Category", ["All"] + CATEGORIES)
    with filter_col5:
        dept_filter = st.selectbox("Department", ["All"] + DEPARTMENTS)

    # Fetch matching tickets
    filtered_tickets = get_all_tickets(
        category=category_filter,
        priority=priority_filter,
        status=status_filter,
        team=dept_filter,
        search=search_query,
    )

    st.markdown(
        f"<div style='font-size: 0.85rem; color: #64748B; margin-bottom: 12px;'>"
        f"Displaying <b>{len(filtered_tickets)}</b> tickets</div>",
        unsafe_allow_html=True,
    )

    if not filtered_tickets:
        st.info("No tickets matched the selected filter criteria.")
    else:
        # Display as interactive selection and table
        df_display = pd.DataFrame(filtered_tickets)
        
        # Quick Table Preview
        table_view = df_display[
            [
                "ticket_id",
                "customer_name",
                "category",
                "priority",
                "assigned_team",
                "status",
                "created_at",
            ]
        ].copy()
        table_view.columns = [
            "ID",
            "Customer",
            "Category",
            "Priority",
            "Department",
            "Status",
            "Created",
        ]
        st.dataframe(table_view, use_container_width=True, hide_index=True)

        st.markdown("---")
        st.markdown("##### 🔍 Inspect & Update Ticket Details")

        ticket_ids = [t["ticket_id"] for t in filtered_tickets]
        selected_id = st.selectbox("Select Ticket ID to View / Edit", options=ticket_ids)

        if selected_id:
            ticket = get_ticket_by_id(selected_id)
            if ticket:
                with st.expander(f"Ticket Details: {ticket['ticket_id']} - {ticket['customer_name']}", expanded=True):
                    col_det1, col_det2 = st.columns([1, 1])

                    with col_det1:
                        st.markdown(f"**Customer:** {ticket['customer_name']}")
                        if ticket.get("customer_email"):
                            st.markdown(f"**Email:** {ticket['customer_email']}")
                        st.markdown(f"**Source:** {ticket['source']}")
                        st.markdown(f"**Created At:** {ticket['created_at']}")
                        st.markdown(f"**Last Updated:** {ticket['updated_at']}")
                        st.text_area("Customer Message", value=ticket["message"], height=100, disabled=True)
                        st.text_area("AI Issue Summary", value=ticket["summary"], height=70, disabled=True)
                        st.info(f"💡 **Recommended Action:** {ticket['recommended_action']}")

                    with col_det2:
                        st.markdown("##### ⚙️ Update Ticket Fields")
                        current_status_idx = (
                            TICKET_STATUSES.index(ticket["status"])
                            if ticket["status"] in TICKET_STATUSES
                            else 0
                        )
                        new_status = st.selectbox(
                            "Ticket Status",
                            options=TICKET_STATUSES,
                            index=current_status_idx,
                            key=f"status_{selected_id}",
                        )

                        current_pri_idx = (
                            PRIORITIES.index(ticket["priority"])
                            if ticket["priority"] in PRIORITIES
                            else 2
                        )
                        new_priority = st.selectbox(
                            "Priority Level",
                            options=PRIORITIES,
                            index=current_pri_idx,
                            key=f"pri_{selected_id}",
                        )

                        current_team_idx = (
                            DEPARTMENTS.index(ticket["assigned_team"])
                            if ticket["assigned_team"] in DEPARTMENTS
                            else 0
                        )
                        new_team = st.selectbox(
                            "Assigned Department",
                            options=DEPARTMENTS,
                            index=current_team_idx,
                            key=f"team_{selected_id}",
                        )

                        col_btn1, col_btn2 = st.columns(2)
                        with col_btn1:
                            if st.button("💾 Save Changes", key=f"save_{selected_id}", use_container_width=True, type="primary"):
                                update_ticket(
                                    selected_id,
                                    {
                                        "status": new_status,
                                        "priority": new_priority,
                                        "assigned_team": new_team,
                                    },
                                )
                                st.success("Ticket updated successfully!")
                                st.rerun()

                        with col_btn2:
                            if st.button("🗑️ Delete Ticket", key=f"del_{selected_id}", use_container_width=True):
                                delete_ticket(selected_id)
                                st.warning(f"Ticket {selected_id} deleted.")
                                st.rerun()


# ==============================================================================
# SECTION 4: AI INSIGHTS & OPERATIONAL INTELLIGENCE
# ==============================================================================
elif nav_selection == "💡 AI Insights":
    st.markdown("<div class='section-header'>💡 AI Operational Insights & Intelligence</div>", unsafe_allow_html=True)
    st.caption("Data-grounded observations calculated from stored tickets to improve customer support operations.")

    tickets = get_all_tickets()
    if not tickets:
        st.info("No ticket data available for analysis. Load demo tickets or create new ones to view operational insights.")
        if st.button("🚀 Load Demo Tickets"):
            insert_demo_tickets(get_demo_tickets())
            st.rerun()
    else:
        df = pd.DataFrame(tickets)
        total = len(df)

        # 1. Top Category
        cat_counts = df["category"].value_counts()
        top_category = cat_counts.index[0]
        top_cat_pct = round((cat_counts.iloc[0] / total) * 100, 1)

        # 2. Top Department
        dept_counts = df["assigned_team"].value_counts()
        top_dept = dept_counts.index[0]
        top_dept_pct = round((dept_counts.iloc[0] / total) * 100, 1)

        # 3. High & Critical Volume
        critical_count = int((df["priority"] == "Critical").sum())
        high_count = int((df["priority"] == "High").sum())
        urgent_pct = round(((critical_count + high_count) / total) * 100, 1)

        # 4. Sentiment Breakdown
        sentiment_counts = df["sentiment"].value_counts()
        neg_count = int((df["sentiment"] == "Negative").sum())
        neg_pct = round((neg_count / total) * 100, 1)

        # Insights Cards
        ic1, ic2, ic3, ic4 = st.columns(4)
        with ic1:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-title">Primary Driver</div>
                    <div class="metric-value" style="font-size: 1.4rem;">{top_category}</div>
                    <div class="metric-subtext">{top_cat_pct}% of total ticket volume</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with ic2:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-title">Busiest Team</div>
                    <div class="metric-value" style="font-size: 1.4rem;">{top_dept}</div>
                    <div class="metric-subtext">{top_dept_pct}% assigned workload</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with ic3:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-title">High & Critical</div>
                    <div class="metric-value" style="color: #DC2626;">{critical_count + high_count}</div>
                    <div class="metric-subtext">{urgent_pct}% require expedited SLA</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with ic4:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-title">Negative Sentiment</div>
                    <div class="metric-value" style="color: #EA580C;">{neg_pct}%</div>
                    <div class="metric-subtext">{neg_count} frustrated or urgent inquiries</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("##### 📌 Data-Grounded Operational Observations")

        # Dynamic Observations based on actual distributions
        observations = []
        if top_category == "Billing Issue":
            observations.append(
                f"💳 **Billing Alert:** Billing issues represent the largest share ({top_cat_pct}%) of current customer inquiries. "
                "The billing support team and payment gateway error rates may warrant review to mitigate customer churn."
            )
        elif top_category == "Product Defect":
            observations.append(
                f"📦 **Quality Assurance Alert:** Product defects represent {top_cat_pct}% of support requests. "
                "Hardware QA teams should inspect recent batch packaging and safety reports."
            )
        elif top_category == "Service Request":
            observations.append(
                f"🌐 **Infrastructure Alert:** Service requests account for {top_cat_pct}% of incoming traffic. "
                "Verify platform availability and upstream cloud dependencies."
            )

        if critical_count > 0:
            observations.append(
                f"🚨 **Safety & Critical Escalation:** {critical_count} ticket(s) are classified as Critical priority. "
                "Mandatory on-call protocol is in effect; review safety hazards and outage reports first."
            )

        if top_dept_pct > 35:
            observations.append(
                f"👥 **Workforce Capacity Warning:** {top_dept} is handling {top_dept_pct}% of all assigned tickets. "
                "Consider rebalancing support agent shift coverage during peak hours."
            )

        # Display observation alerts
        for obs in observations:
            st.markdown(
                f"<div style='background-color: #F8FAFC; border-left: 4px solid #2563EB; "
                f"border-radius: 6px; padding: 14px 18px; margin-bottom: 12px; color: #1E293B;'>"
                f"{obs}</div>",
                unsafe_allow_html=True,
            )

        st.markdown("<br>", unsafe_allow_html=True)
        
        # Sentiment & Priority breakdown charts
        chart_col1, chart_col2 = st.columns(2)
        with chart_col1:
            sent_df = df["sentiment"].value_counts().reset_index()
            sent_df.columns = ["Sentiment", "Count"]
            fig_sent = px.bar(
                sent_df,
                x="Sentiment",
                y="Count",
                title="Customer Sentiment Distribution",
                color="Sentiment",
                color_discrete_map=SENTIMENT_COLORS,
                text="Count",
            )
            fig_sent.update_layout(
                showlegend=False,
                margin=dict(l=20, r=20, t=40, b=20),
                xaxis_title="",
                yaxis_title="Count",
            )
            fig_sent.update_traces(textposition="outside")
            st.plotly_chart(fig_sent, use_container_width=True)

        with chart_col2:
            # Cross-tab of Category vs Priority
            ct = pd.crosstab(df["category"], df["priority"]).reset_index()
            fig_ct = px.bar(
                ct,
                x="category",
                y=[c for c in PRIORITIES if c in ct.columns],
                title="Priority Breakdown per Category",
                color_discrete_map=PRIORITY_COLORS,
                barmode="stack",
            )
            fig_ct.update_layout(
                margin=dict(l=20, r=20, t=40, b=20),
                xaxis_title="",
                yaxis_title="Tickets",
                legend_title="Priority",
            )
            st.plotly_chart(fig_ct, use_container_width=True)


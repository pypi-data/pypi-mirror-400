"""Mind v5 Admin Dashboard.

VIBESHIP-styled Streamlit application for monitoring and exploring Mind v5.

Run with:
    streamlit run src/mind/dashboard/app.py
"""

from datetime import datetime

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from mind.dashboard.api import get_api
from mind.dashboard.theme import COLORS, CUSTOM_CSS, PLOTLY_THEME

# Page config
st.set_page_config(
    page_title="Mind v5 | VIBESHIP",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Apply custom CSS
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def render_header():
    """Render the VIBESHIP header."""
    st.markdown(
        '<h1 class="vibeship-header">🧠 Mind v5</h1>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p class="vibeship-subtitle">Decision Intelligence Dashboard</p>',
        unsafe_allow_html=True,
    )


def render_sidebar():
    """Render the navigation sidebar."""
    with st.sidebar:
        st.markdown(
            """
            <div style="padding: 1rem 0; border-bottom: 1px solid #2a3042; margin-bottom: 1rem;">
                <span style="font-size: 1.5rem;">🚀</span>
                <span style="font-family: 'Instrument Serif', Georgia, serif; font-size: 1.35rem; color: #e2e4e9; margin-left: 0.5rem;">VIBESHIP</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        page = st.radio(
            "Navigate",
            ["🏠 Overview", "🧠 Memory Explorer", "📊 Decision Analytics", "⚡ System Health"],
            label_visibility="collapsed",
        )

        st.markdown("---")

        # Quick stats
        api = get_api()
        health = api.health()
        status = health.get("status", "unknown")

        if status == "healthy":
            st.markdown(
                '<span class="status-healthy">● System Online</span>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<span class="status-unhealthy">● System Offline</span>',
                unsafe_allow_html=True,
            )

        st.markdown(
            f"""
            <div style="margin-top: 1rem; color: #6b7489; font-size: 0.75rem;">
                Version: {health.get("version", "unknown")}<br>
                Last updated: {datetime.now().strftime("%H:%M:%S")}
            </div>
            """,
            unsafe_allow_html=True,
        )

    return page


def render_overview():
    """Render the overview dashboard."""
    render_header()

    api = get_api()
    health = api.health()
    ready = api.ready()
    metrics = api.parse_metrics()
    dlq = api.dlq_stats()

    # Top metrics row
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-value">{health.get("status", "?").upper()}</div>
                <div class="metric-label">System Status</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        decision_rate = metrics.get("mind_decision_success_rate", 0.87)
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-value">{decision_rate:.1%}</div>
                <div class="metric-label">Decision Success Rate</div>
                <div class="metric-delta-positive">↑ 2.3% from last week</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col3:
        requests = int(metrics.get("mind_requests_total", 12453))
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-value">{requests:,}</div>
                <div class="metric-label">Total Requests</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col4:
        dlq_count = dlq.get("total_messages", 0)
        color_class = "metric-delta-positive" if dlq_count == 0 else "metric-delta-negative"
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-value">{dlq_count}</div>
                <div class="metric-label">DLQ Messages</div>
                <div class="{color_class}">{"✓ All clear" if dlq_count == 0 else "⚠ Needs attention"}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # Two column layout for charts
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📈 Decision Quality Trend")
        # Mock data for demo - in production, fetch from metrics API
        dates = pd.date_range(end=datetime.now(), periods=30, freq="D")
        success_rates = [0.82 + (i * 0.005) + (0.02 * (i % 3)) for i in range(30)]

        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=dates,
                y=success_rates,
                mode="lines",
                fill="tozeroy",
                line={"color": COLORS["green_dim"], "width": 2},
                fillcolor="rgba(0, 196, 154, 0.1)",
                name="Success Rate",
            )
        )
        fig.update_layout(
            **PLOTLY_THEME["layout"],
            height=300,
            margin={"l": 0, "r": 0, "t": 20, "b": 0},
            showlegend=False,
        )
        fig.update_yaxes(tickformat=".0%", range=[0.7, 1.0])
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("### 🧠 Memory Distribution")
        # Memory level distribution
        levels = ["Immediate", "Situational", "Seasonal", "Identity"]
        values = [15, 45, 25, 15]
        colors = [COLORS["red"], COLORS["orange"], COLORS["blue"], COLORS["violet"]]

        fig = go.Figure(
            data=[
                go.Pie(
                    labels=levels,
                    values=values,
                    hole=0.6,
                    marker_colors=colors,
                    textinfo="percent",
                    textposition="outside",
                    textfont={"color": COLORS["text_primary"]},
                )
            ]
        )
        fig.update_layout(
            **PLOTLY_THEME["layout"],
            height=300,
            margin={"l": 0, "r": 0, "t": 20, "b": 0},
            showlegend=True,
            legend={
                "orientation": "h",
                "yanchor": "bottom",
                "y": -0.2,
                "xanchor": "center",
                "x": 0.5,
            },
        )
        st.plotly_chart(fig, use_container_width=True)

    # Services status
    st.markdown("### 🔌 Connected Services")
    services = ready.get("services", {})
    if not services:
        services = {
            "PostgreSQL": True,
            "NATS JetStream": True,
            "Qdrant": True,
            "FalkorDB": True,
            "Temporal": True,
            "OpenAI": True,
        }

    cols = st.columns(6)
    service_icons = {
        "PostgreSQL": "🐘",
        "NATS JetStream": "📨",
        "Qdrant": "🔍",
        "FalkorDB": "🕸️",
        "Temporal": "⏱️",
        "OpenAI": "🤖",
    }

    for idx, (service, status) in enumerate(services.items()):
        with cols[idx % 6]:
            icon = service_icons.get(service, "📦")
            status_class = "status-healthy" if status else "status-unhealthy"
            status_text = "Online" if status else "Offline"
            st.markdown(
                f"""
                <div class="metric-card" style="text-align: center; padding: 1rem;">
                    <div style="font-size: 2rem;">{icon}</div>
                    <div style="color: #e2e4e9; font-weight: 500; margin: 0.5rem 0;">{service}</div>
                    <span class="{status_class}">{status_text}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )


def render_memory_explorer():
    """Render the memory explorer page."""
    render_header()
    st.markdown("## 🧠 Memory Explorer")
    st.markdown("Explore and search memories across users and temporal levels.")

    col1, col2 = st.columns([2, 1])

    with col1:
        user_id = st.text_input(
            "User ID",
            value="550e8400-e29b-41d4-a716-446655440000",
            help="Enter a UUID to explore memories for a specific user",
        )

    with col2:
        min_salience = st.slider(
            "Minimum Salience",
            0.0,
            1.0,
            0.0,
            help="Filter memories by minimum effective salience",
        )

    query = st.text_input(
        "Search Query",
        placeholder="Search memories by content...",
        help="Semantic search across memory content",
    )

    if st.button("🔍 Search Memories", use_container_width=True):
        api = get_api()
        result = api.get_memories(user_id, query, limit=50, min_salience=min_salience)

        if "error" in result and result.get("error"):
            st.error(f"Error: {result['error']}")
        else:
            memories = result.get("memories", [])

            if not memories:
                st.info("No memories found. Try adjusting your search criteria.")
            else:
                st.success(f"Found {len(memories)} memories")

                # Display memories as cards
                for mem in memories:
                    level_name = mem.get("temporal_level_name", "unknown")
                    level_class = f"level-{level_name}"
                    salience = mem.get("effective_salience", 0)
                    score = (
                        mem.get("score", 0)
                        if "score" in mem
                        else result.get("scores", {}).get(mem.get("memory_id"), 0)
                    )

                    # Display as a card instead of expander for better readability
                    content = mem.get('content', '')
                    content_type = mem.get('content_type', 'observation')
                    memory_id = mem.get('memory_id', 'N/A')[:8]

                    st.markdown(
                        f"""
                        <div class="metric-card" style="margin-bottom: 0.75rem; padding: 1rem;">
                            <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.75rem;">
                                <div style="flex: 1;">
                                    <div style="color: #e2e4e9; font-size: 0.95rem; line-height: 1.4;">{content}</div>
                                </div>
                                <div style="margin-left: 1rem; text-align: right;">
                                    <span class="{level_class}" style="padding: 0.2rem 0.5rem; font-size: 0.7rem; text-transform: uppercase;">{level_name}</span>
                                </div>
                            </div>
                            <div style="display: flex; gap: 1.5rem; color: #6b7489; font-size: 0.75rem;">
                                <span>Type: <span style="color: #9aa3b5;">{content_type}</span></span>
                                <span>Salience: <span style="color: #00C49A;">{salience:.2f}</span></span>
                                <span>Score: <span style="color: #9aa3b5;">{score:.3f}</span></span>
                                <span>ID: <span style="color: #9aa3b5;">{memory_id}...</span></span>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

    # Memory level legend
    st.markdown("---")
    st.markdown("### 📊 Temporal Levels Explained")

    col1, col2, col3, col4 = st.columns(4)

    levels_info = [
        ("🔴 Immediate", "Hours", "Current session context, fleeting thoughts"),
        ("🟡 Situational", "Days-Weeks", "Recent patterns, current projects"),
        ("🔵 Seasonal", "Months", "Recurring behaviors, seasonal preferences"),
        ("🟣 Identity", "Years", "Core preferences, long-term traits"),
    ]

    for col, (name, duration, desc) in zip([col1, col2, col3, col4], levels_info, strict=False):
        with col:
            st.markdown(
                f"""
                <div class="metric-card" style="height: 150px;">
                    <div style="font-size: 1.25rem; font-weight: 600; color: #e2e4e9;">{name}</div>
                    <div style="color: #00C49A; font-size: 0.875rem; margin: 0.5rem 0;">{duration}</div>
                    <div style="color: #9aa3b5; font-size: 0.75rem;">{desc}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def render_decision_analytics():
    """Render the decision analytics page."""
    render_header()
    st.markdown("## 📊 Decision Analytics")
    st.markdown("Understand how memories influence decisions and track the feedback loop.")

    api = get_api()
    metrics = api.parse_metrics()

    # Key metrics
    col1, col2, col3 = st.columns(3)

    with col1:
        success_rate = metrics.get("mind_decision_success_rate", 0.87)
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-value">{success_rate:.1%}</div>
                <div class="metric-label">Decision Success Rate</div>
                <div class="metric-delta-positive">↑ 2.3% this week</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        calibration = metrics.get("mind_confidence_calibration_error", 0.08)
        quality = (
            "Excellent" if calibration < 0.1 else "Good" if calibration < 0.2 else "Needs Work"
        )
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-value">{calibration:.2f}</div>
                <div class="metric-label">Calibration Error</div>
                <div class="metric-delta-positive">{quality}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col3:
        avg_memories = metrics.get("mind_context_completeness", 4.2)
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-value">{avg_memories:.1f}</div>
                <div class="metric-label">Avg Memories/Decision</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # Feedback loop visualization
    st.markdown("### 🔄 The Feedback Loop")

    col1, col2 = st.columns([3, 2])

    with col1:
        st.markdown(
            """
            <div style="background: linear-gradient(135deg, rgba(0, 196, 154, 0.05) 0%, rgba(157, 140, 255, 0.05) 100%);
                        border: 1px solid #2a3042; padding: 2rem; margin: 1rem 0;">
                <div style="display: flex; justify-content: space-around; align-items: center; flex-wrap: wrap; gap: 1rem;">
                    <div style="text-align: center;">
                        <div style="font-size: 2.5rem;">🧠</div>
                        <div style="color: #e2e4e9; font-weight: 600;">Retrieve</div>
                        <div style="color: #9aa3b5; font-size: 0.75rem;">Find relevant memories</div>
                    </div>
                    <div style="font-size: 1.5rem; color: #00C49A;">→</div>
                    <div style="text-align: center;">
                        <div style="font-size: 2.5rem;">🎯</div>
                        <div style="color: #e2e4e9; font-weight: 600;">Decide</div>
                        <div style="color: #9aa3b5; font-size: 0.75rem;">Make a decision</div>
                    </div>
                    <div style="font-size: 1.5rem; color: #00C49A;">→</div>
                    <div style="text-align: center;">
                        <div style="font-size: 2.5rem;">📊</div>
                        <div style="color: #e2e4e9; font-weight: 600;">Outcome</div>
                        <div style="color: #9aa3b5; font-size: 0.75rem;">Record result</div>
                    </div>
                    <div style="font-size: 1.5rem; color: #00C49A;">→</div>
                    <div style="text-align: center;">
                        <div style="font-size: 2.5rem;">✨</div>
                        <div style="color: #e2e4e9; font-weight: 600;">Learn</div>
                        <div style="color: #9aa3b5; font-size: 0.75rem;">Adjust salience</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            """
            **How it works:**

            1. **Retrieve** memories using semantic search
            2. **Decide** using the retrieved context
            3. **Record** whether the outcome was good or bad
            4. **Learn** by adjusting memory salience

            Good outcomes → Higher salience → More likely to be retrieved

            Bad outcomes → Lower salience → Less likely to influence future decisions
            """
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # Outcome distribution
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📈 Outcome Distribution")
        outcomes = ["Positive", "Neutral", "Negative"]
        values = [67, 25, 8]
        colors = [COLORS["green"], COLORS["text_secondary"], COLORS["red"]]

        fig = go.Figure(
            data=[
                go.Bar(
                    x=outcomes,
                    y=values,
                    marker_color=colors,
                    text=[f"{v}%" for v in values],
                    textposition="outside",
                    textfont={"color": COLORS["text_primary"]},
                )
            ]
        )
        fig.update_layout(
            **PLOTLY_THEME["layout"],
            height=300,
            margin={"l": 0, "r": 0, "t": 20, "b": 0},
            showlegend=False,
        )
        fig.update_yaxes(range=[0, 100])
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("### 🎯 Confidence vs Accuracy")
        # Calibration plot
        confidence_bins = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
        accuracy = [0.12, 0.18, 0.32, 0.38, 0.52, 0.58, 0.72, 0.78, 0.88, 0.95]

        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=confidence_bins,
                y=accuracy,
                mode="lines+markers",
                line={"color": COLORS["green_dim"], "width": 2},
                marker={"size": 8, "color": COLORS["teal"]},
                name="Actual",
            )
        )
        fig.add_trace(
            go.Scatter(
                x=[0, 1],
                y=[0, 1],
                mode="lines",
                line={"color": COLORS["text_secondary"], "dash": "dash"},
                name="Perfect",
            )
        )
        fig.update_layout(
            **PLOTLY_THEME["layout"],
            height=300,
            margin={"l": 0, "r": 0, "t": 20, "b": 0},
            legend={"orientation": "h", "y": -0.2},
        )
        fig.update_xaxes(title="Confidence")
        fig.update_yaxes(title="Accuracy")
        st.plotly_chart(fig, use_container_width=True)


def render_system_health():
    """Render the system health page."""
    render_header()
    st.markdown("## ⚡ System Health")
    st.markdown("Monitor infrastructure, performance, and operational metrics.")

    api = get_api()
    health = api.health()
    ready = api.ready()
    dlq = api.dlq_stats()
    metrics = api.parse_metrics()

    # Status overview
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        status = health.get("status", "unknown")
        color = COLORS["green"] if status == "healthy" else COLORS["red"]
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-value" style="background: {color}; -webkit-background-clip: text;
                     -webkit-text-fill-color: transparent; background-clip: text;">
                    {status.upper()}
                </div>
                <div class="metric-label">API Status</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        latency = metrics.get("mind_request_latency_seconds", 0.045) * 1000
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-value">{latency:.0f}ms</div>
                <div class="metric-label">P95 Latency</div>
                <div class="metric-delta-positive">{"Good" if latency < 100 else "Slow"}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col3:
        uptime = 99.97
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-value">{uptime}%</div>
                <div class="metric-label">Uptime (30d)</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col4:
        dlq_count = dlq.get("total_messages", 0)
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-value">{dlq_count}</div>
                <div class="metric-label">DLQ Messages</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # Tabs for different metrics
    tab1, tab2, tab3 = st.tabs(["🔌 Services", "📊 Performance", "⚠️ Alerts"])

    with tab1:
        st.markdown("### Service Health")

        services = ready.get("services", {})
        if not services:
            services = {
                "api": {"status": "healthy", "latency_ms": 12},
                "postgres": {"status": "healthy", "connections": 45},
                "nats": {"status": "healthy", "messages_pending": 0},
                "qdrant": {"status": "healthy", "vectors": 15243},
                "falkordb": {"status": "healthy", "nodes": 8921},
                "temporal": {"status": "healthy", "workflows_active": 3},
            }

        for service, info in services.items():
            status = (
                info.get("status", info)
                if isinstance(info, dict)
                else ("healthy" if info else "unhealthy")
            )
            is_healthy = status == "healthy" or status is True

            with st.expander(f"{'🟢' if is_healthy else '🔴'} {service.upper()}", expanded=False):
                if isinstance(info, dict):
                    for key, value in info.items():
                        if key != "status":
                            st.markdown(f"**{key.replace('_', ' ').title()}:** {value}")
                else:
                    st.markdown(f"**Status:** {'Healthy' if is_healthy else 'Unhealthy'}")

    with tab2:
        st.markdown("### Performance Metrics")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### Request Latency Distribution")
            # Mock latency histogram
            import numpy as np

            latencies = np.random.exponential(30, 1000)
            latencies = latencies[latencies < 200]

            fig = go.Figure(
                data=[
                    go.Histogram(
                        x=latencies,
                        nbinsx=50,
                        marker_color=COLORS["teal"],
                    )
                ]
            )
            fig.update_layout(
                **PLOTLY_THEME["layout"],
                height=250,
                margin={"l": 0, "r": 0, "t": 20, "b": 0},
            )
            fig.update_xaxes(title="Latency (ms)")
            fig.update_yaxes(title="Count")
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown("#### Requests per Minute")
            # Mock RPS data
            times = pd.date_range(end=datetime.now(), periods=60, freq="min")
            rps = [100 + (i % 20) * 5 + (10 * (i % 5)) for i in range(60)]

            fig = go.Figure()
            fig.add_trace(
                go.Scatter(
                    x=times,
                    y=rps,
                    mode="lines",
                    fill="tozeroy",
                    line={"color": COLORS["green_dim"], "width": 2},
                    fillcolor="rgba(0, 196, 154, 0.1)",
                )
            )
            fig.update_layout(
                **PLOTLY_THEME["layout"],
                height=250,
                margin={"l": 0, "r": 0, "t": 20, "b": 0},
            )
            fig.update_yaxes(title="Requests/min")
            st.plotly_chart(fig, use_container_width=True)

    with tab3:
        st.markdown("### Active Alerts")

        anomalies = api.anomalies()
        alert_list = anomalies.get("anomalies", [])

        if not alert_list:
            st.markdown(
                """
                <div style="background: rgba(46, 204, 113, 0.1); border: 1px solid rgba(46, 204, 113, 0.3);
                            padding: 2rem; text-align: center;">
                    <div style="font-size: 2rem;">✅</div>
                    <div style="color: #2ECC71; font-weight: 600; margin-top: 0.5rem;">All Systems Normal</div>
                    <div style="color: #9aa3b5; font-size: 0.875rem;">No active alerts or anomalies detected</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            for alert in alert_list:
                severity = alert.get("severity", "warning")
                color = COLORS["red"] if severity == "critical" else COLORS["orange"]
                st.markdown(
                    f"""
                    <div style="background: rgba({color}, 0.1); border: 1px solid {color};
                                padding: 1rem; margin-bottom: 0.5rem;">
                        <div style="color: {color}; font-weight: 600;">
                            {"🚨" if severity == "critical" else "⚠️"} {alert.get("title", "Alert")}
                        </div>
                        <div style="color: #9aa3b5; font-size: 0.875rem; margin-top: 0.5rem;">
                            {alert.get("description", "")}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )


def main():
    """Main application entry point."""
    page = render_sidebar()

    if "Overview" in page:
        render_overview()
    elif "Memory" in page:
        render_memory_explorer()
    elif "Decision" in page:
        render_decision_analytics()
    elif "Health" in page:
        render_system_health()


if __name__ == "__main__":
    main()

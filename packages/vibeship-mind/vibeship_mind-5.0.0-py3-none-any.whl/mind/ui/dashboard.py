"""
Mind v5 Admin Dashboard

A Streamlit-based admin interface for the Mind v5 decision intelligence system.

Run with: streamlit run src/mind/ui/dashboard.py
"""

import json
from datetime import datetime
from uuid import uuid4

import httpx
import pandas as pd
import plotly.express as px
import streamlit as st

# Configuration
API_BASE = "http://localhost:8001"

st.set_page_config(
    page_title="Mind v5 Admin",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)


def get_client() -> httpx.Client:
    """Get HTTP client for API calls."""
    return httpx.Client(base_url=API_BASE, timeout=30.0)


# --- Sidebar ---
with st.sidebar:
    st.title("🧠 Mind v5")
    st.caption("Decision Intelligence System")
    st.divider()

    # Health status
    st.subheader("System Status")
    try:
        with get_client() as client:
            health = client.get("/health").json()
            ready = client.get("/ready").json()

        if health["status"] == "healthy":
            st.success(f"API: {health['status']} (v{health['version']})")
        else:
            st.error(f"API: {health['status']}")

        # Component status
        components = {
            "Database": ready["database"],
            "NATS": ready["nats"],
            "FalkorDB": ready["falkordb"],
            "Temporal": ready["temporal"],
        }
        if ready.get("qdrant"):
            components["Qdrant"] = ready["qdrant"]

        for name, status in components.items():
            if status == "connected":
                st.write(f"✅ {name}")
            elif status == "not_configured":
                st.write(f"⚪ {name} (optional)")
            else:
                st.write(f"❌ {name}: {status}")

    except httpx.ConnectError:
        st.error("Cannot connect to API")
        st.info("Start the API with: `uvicorn mind.api.app:app`")

    st.divider()
    st.caption("Navigate using tabs above")


# --- Main Content ---
tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["📊 Overview", "🧠 Memories", "🎯 Decisions", "⚠️ Anomalies", "🔧 Tools"]
)


# --- Tab 1: Overview ---
with tab1:
    st.header("System Overview")

    col1, col2, col3, col4 = st.columns(4)

    try:
        with get_client() as client:
            # Get some stats
            ready = client.get("/ready").json()

            with col1:
                st.metric("API Status", "Online" if ready["ready"] else "Degraded")

            with col2:
                st.metric("Database", ready["database"].title())

            with col3:
                st.metric("Event Bus", ready["nats"].title())

            with col4:
                st.metric("Workflows", ready["temporal"].title())

    except Exception as e:
        st.error(f"Failed to fetch stats: {e}")

    st.divider()

    # Recent activity placeholder
    st.subheader("Quick Actions")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Create Test Memory")
        with st.form("quick_memory"):
            content = st.text_area("Content", "This is a test memory from the dashboard")
            temporal_level = st.selectbox(
                "Temporal Level",
                options=[1, 2, 3, 4],
                format_func=lambda x: {
                    1: "Working (hours)",
                    2: "Recent (days)",
                    3: "Reference (weeks)",
                    4: "Identity (permanent)",
                }[x],
            )
            if st.form_submit_button("Create Memory"):
                try:
                    with get_client() as client:
                        user_id = str(uuid4())
                        resp = client.post(
                            "/v1/memories/",
                            json={
                                "user_id": user_id,
                                "content": content,
                                "temporal_level": temporal_level,
                            },
                        )
                        if resp.status_code == 200:
                            data = resp.json()
                            st.success(f"Created memory: {data['memory_id'][:8]}...")
                            st.json(data)
                        else:
                            st.error(f"Failed: {resp.text}")
                except Exception as e:
                    st.error(f"Error: {e}")

    with col2:
        st.markdown("### Test Retrieval")
        with st.form("quick_retrieve"):
            user_id = st.text_input("User ID (UUID)", str(uuid4()))
            query = st.text_input("Query", "test memory")
            if st.form_submit_button("Retrieve"):
                try:
                    with get_client() as client:
                        resp = client.post(
                            "/v1/memories/retrieve",
                            json={"user_id": user_id, "query": query, "limit": 5},
                        )
                        if resp.status_code == 200:
                            data = resp.json()
                            if data["memories"]:
                                st.success(f"Found {len(data['memories'])} memories")
                                for m in data["memories"]:
                                    st.write(
                                        f"- {m['content'][:50]}... (score: {m.get('score', 'N/A')})"
                                    )
                            else:
                                st.info("No memories found")
                        else:
                            st.error(f"Failed: {resp.text}")
                except Exception as e:
                    st.error(f"Error: {e}")


# --- Tab 2: Memories ---
with tab2:
    st.header("Memory Management")

    # Create memory form
    with st.expander("➕ Create New Memory", expanded=False), st.form("create_memory"):
        col1, col2 = st.columns(2)

        with col1:
            user_id = st.text_input("User ID", str(uuid4()), key="mem_user")
            content = st.text_area("Memory Content", height=100)

        with col2:
            temporal_level = st.selectbox(
                "Temporal Level",
                options=[1, 2, 3, 4],
                format_func=lambda x: {
                    1: "Working (hours)",
                    2: "Recent (days)",
                    3: "Reference (weeks)",
                    4: "Identity (permanent)",
                }[x],
                key="mem_level",
            )
            salience = st.slider("Base Salience", 0.0, 1.0, 0.5)

        submitted = st.form_submit_button("Create Memory")

        if submitted and content:
            try:
                with get_client() as client:
                    resp = client.post(
                        "/v1/memories/",
                        json={
                            "user_id": user_id,
                            "content": content,
                            "temporal_level": temporal_level,
                            "base_salience": salience,
                        },
                    )
                    if resp.status_code == 200:
                        st.success("Memory created!")
                        st.json(resp.json())
                    else:
                        st.error(f"Error: {resp.text}")
            except Exception as e:
                st.error(f"Failed: {e}")

    # Retrieve memories
    st.subheader("Search Memories")

    col1, col2 = st.columns([2, 1])

    with col1:
        search_user = st.text_input("User ID to search", key="search_user")
        search_query = st.text_input("Search query", key="search_query")

    with col2:
        search_limit = st.number_input("Limit", 1, 50, 10)
        search_btn = st.button("🔍 Search")

    if search_btn and search_user and search_query:
        try:
            with get_client() as client:
                resp = client.post(
                    "/v1/memories/retrieve",
                    json={
                        "user_id": search_user,
                        "query": search_query,
                        "limit": search_limit,
                    },
                )
                if resp.status_code == 200:
                    data = resp.json()
                    memories = data.get("memories", [])

                    if memories:
                        st.success(f"Found {len(memories)} memories")

                        # Display as dataframe
                        df = pd.DataFrame(memories)
                        if not df.empty:
                            display_cols = ["content", "temporal_level", "base_salience"]
                            available_cols = [c for c in display_cols if c in df.columns]
                            if available_cols:
                                st.dataframe(df[available_cols], use_container_width=True)

                            # Show full details in expander
                            for i, mem in enumerate(memories):
                                with st.expander(
                                    f"Memory {i + 1}: {mem.get('content', '')[:50]}..."
                                ):
                                    st.json(mem)
                    else:
                        st.info("No memories found matching your query")
                else:
                    st.error(f"Search failed: {resp.text}")
        except Exception as e:
            st.error(f"Error: {e}")


# --- Tab 3: Decisions ---
with tab3:
    st.header("Decision Tracking")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Track New Decision")
        with st.form("track_decision"):
            user_id = st.text_input("User ID", str(uuid4()), key="dec_user")
            session_id = st.text_input("Session ID", str(uuid4()), key="dec_session")
            query = st.text_input("Decision Query", "What should I do?")
            context = st.text_area("Context", "User is making a decision")

            if st.form_submit_button("Track Decision"):
                try:
                    with get_client() as client:
                        resp = client.post(
                            "/v1/decisions/track",
                            json={
                                "user_id": user_id,
                                "session_id": session_id,
                                "query": query,
                                "context": context,
                            },
                        )
                        if resp.status_code == 200:
                            data = resp.json()
                            st.success("Decision tracked!")
                            st.session_state["last_trace_id"] = data.get("trace_id")
                            st.json(data)
                        else:
                            st.error(f"Error: {resp.text}")
                except Exception as e:
                    st.error(f"Failed: {e}")

    with col2:
        st.subheader("Record Outcome")
        with st.form("record_outcome"):
            trace_id = st.text_input(
                "Trace ID",
                st.session_state.get("last_trace_id", ""),
                key="out_trace",
            )
            quality = st.slider("Outcome Quality", -1.0, 1.0, 0.5, 0.1)
            signal = st.selectbox("Signal", ["positive", "negative", "neutral"])
            feedback = st.text_area("Feedback (optional)", "")

            if st.form_submit_button("Record Outcome"):
                if not trace_id:
                    st.warning("Please enter a trace ID")
                else:
                    try:
                        with get_client() as client:
                            resp = client.post(
                                "/v1/decisions/outcome",
                                json={
                                    "trace_id": trace_id,
                                    "quality": quality,
                                    "signal": signal,
                                    "feedback": feedback if feedback else None,
                                },
                            )
                            if resp.status_code == 200:
                                st.success("Outcome recorded!")
                                st.json(resp.json())
                            else:
                                st.error(f"Error: {resp.text}")
                    except Exception as e:
                        st.error(f"Failed: {e}")

    st.divider()

    # Lookup decision
    st.subheader("Lookup Decision")
    lookup_trace = st.text_input("Trace ID to lookup", key="lookup_trace")
    if st.button("Lookup") and lookup_trace:
        try:
            with get_client() as client:
                resp = client.get(f"/v1/decisions/{lookup_trace}")
                if resp.status_code == 200:
                    st.json(resp.json())
                else:
                    st.error(f"Not found: {resp.text}")
        except Exception as e:
            st.error(f"Failed: {e}")


# --- Tab 4: Anomalies ---
with tab4:
    st.header("Anomaly Detection")

    col1, col2 = st.columns([1, 3])

    with col1:
        time_window = st.number_input("Time Window (hours)", 1, 168, 24)
        user_filter = st.text_input("User ID (optional)", "")
        run_detection = st.button("🔍 Run Detection")

    with col2:
        if run_detection:
            try:
                with get_client() as client:
                    params = {"time_window_hours": time_window}
                    if user_filter:
                        params["user_id"] = user_filter

                    resp = client.get("/anomalies", params=params)

                    if resp.status_code == 200:
                        data = resp.json()
                        summary = data.get("summary", {})

                        # Summary metrics
                        cols = st.columns(5)
                        cols[0].metric("Total", summary.get("total", 0))
                        cols[1].metric("Critical", summary.get("critical", 0))
                        cols[2].metric("High", summary.get("high", 0))
                        cols[3].metric("Medium", summary.get("medium", 0))
                        cols[4].metric("Low", summary.get("low", 0))

                        # Details
                        anomalies = data.get("anomalies", [])
                        if anomalies:
                            st.warning(f"Found {len(anomalies)} anomalies")

                            # Create visualization
                            severity_counts = {}
                            for a in anomalies:
                                sev = a.get("severity", "unknown")
                                severity_counts[sev] = severity_counts.get(sev, 0) + 1

                            if severity_counts:
                                fig = px.pie(
                                    values=list(severity_counts.values()),
                                    names=list(severity_counts.keys()),
                                    title="Anomalies by Severity",
                                    color_discrete_map={
                                        "critical": "#ff0000",
                                        "high": "#ff6600",
                                        "medium": "#ffcc00",
                                        "low": "#00cc00",
                                    },
                                )
                                st.plotly_chart(fig, use_container_width=True)

                            # List anomalies
                            for a in anomalies:
                                severity = a.get("severity", "unknown")
                                icon = {
                                    "critical": "🔴",
                                    "high": "🟠",
                                    "medium": "🟡",
                                    "low": "🟢",
                                }.get(severity, "⚪")

                                with st.expander(
                                    f"{icon} {a.get('type', 'Unknown')} - {severity.upper()}"
                                ):
                                    st.write(a.get("message", "No message"))
                                    if a.get("details"):
                                        st.json(a["details"])
                        else:
                            st.success("No anomalies detected!")

                        st.caption(f"Checked at: {data.get('checked_at', 'N/A')}")
                    else:
                        st.error(f"Failed: {resp.text}")
            except Exception as e:
                st.error(f"Error: {e}")


# --- Tab 5: Tools ---
with tab5:
    st.header("Admin Tools")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Causal Attribution")
        with st.form("causal_attr"):
            trace_id = st.text_input("Decision Trace ID", key="causal_trace")
            if st.form_submit_button("Get Attribution") and trace_id:
                try:
                    with get_client() as client:
                        resp = client.get(f"/v1/causal/attribution/{trace_id}")
                        if resp.status_code == 200:
                            st.json(resp.json())
                        else:
                            st.error(f"Error: {resp.text}")
                except Exception as e:
                    st.error(f"Failed: {e}")

        st.divider()

        st.subheader("Counterfactual Analysis")
        with st.form("counterfactual"):
            cf_trace = st.text_input("Decision Trace ID", key="cf_trace")
            cf_change = st.text_area(
                "Hypothetical Change (JSON)",
                '{"removed_memory_ids": []}',
            )
            if st.form_submit_button("Analyze") and cf_trace:
                try:
                    change_data = json.loads(cf_change)
                    with get_client() as client:
                        resp = client.post(
                            "/v1/causal/counterfactual",
                            json={"trace_id": cf_trace, **change_data},
                        )
                        if resp.status_code == 200:
                            st.json(resp.json())
                        else:
                            st.error(f"Error: {resp.text}")
                except json.JSONDecodeError:
                    st.error("Invalid JSON")
                except Exception as e:
                    st.error(f"Failed: {e}")

    with col2:
        st.subheader("System Info")
        if st.button("Refresh System Status"):
            try:
                with get_client() as client:
                    resp = client.get("/v1/admin/status")
                    if resp.status_code == 200:
                        st.json(resp.json())
                    else:
                        st.warning("Admin endpoint may require authentication")
            except Exception as e:
                st.error(f"Failed: {e}")

        st.divider()

        st.subheader("Dead Letter Queue")
        if st.button("Check DLQ Stats"):
            try:
                with get_client() as client:
                    resp = client.get("/v1/admin/dlq/stats")
                    if resp.status_code == 200:
                        data = resp.json()
                        st.metric("DLQ Messages", data.get("count", 0))
                        if data.get("count", 0) > 0:
                            st.warning("There are failed messages in the DLQ")
                    else:
                        st.info("DLQ stats unavailable")
            except Exception as e:
                st.error(f"Failed: {e}")

        st.divider()

        st.subheader("Event Stream Info")
        if st.button("Get Event Stream Info"):
            try:
                with get_client() as client:
                    resp = client.get("/v1/admin/events/info")
                    if resp.status_code == 200:
                        st.json(resp.json())
                    else:
                        st.info("Event stream info unavailable")
            except Exception as e:
                st.error(f"Failed: {e}")


# --- Footer ---
st.divider()
st.caption(
    f"Mind v5 Admin Dashboard | API: {API_BASE} | "
    f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
)

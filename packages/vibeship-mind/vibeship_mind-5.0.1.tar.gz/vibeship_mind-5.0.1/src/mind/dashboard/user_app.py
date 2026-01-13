"""Mind v5 User Dashboard.

A beautiful, engaging UI for users to explore their memories.
VIBESHIP-styled with visual flair that makes users want to stay.

Run with:
    streamlit run src/mind/dashboard/user_app.py
"""

import random
import os
from datetime import datetime, timedelta
from uuid import UUID

import httpx
import plotly.graph_objects as go
import streamlit as st

from mind.dashboard.theme import COLORS, CUSTOM_CSS, PLOTLY_THEME

# Configuration
API_BASE = os.environ.get("MIND_API_URL", "http://127.0.0.1:8001")
DEFAULT_USER_ID = os.environ.get("MIND_USER_ID", "550e8400-e29b-41d4-a716-446655440000")

# Page config
st.set_page_config(
    page_title="Mind | Your Memory Universe",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Enhanced CSS for user dashboard
USER_CSS = CUSTOM_CSS + """
<style>
    /* Animated gradient background */
    .stApp {
        background: linear-gradient(135deg, #0e1016 0%, #151820 50%, #0e1016 100%) !important;
    }

    /* Hero section */
    .hero-container {
        text-align: center;
        padding: 2rem 0 3rem 0;
        position: relative;
    }

    .hero-title {
        font-family: 'Instrument Serif', Georgia, serif;
        font-size: 3.5rem;
        font-weight: 400;
        background: linear-gradient(135deg, #e2e4e9 0%, #00C49A 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.5rem;
        animation: fadeInUp 0.8s ease-out;
    }

    .hero-subtitle {
        font-family: 'JetBrains Mono', monospace;
        color: #6b7489;
        font-size: 1rem;
        animation: fadeInUp 0.8s ease-out 0.2s backwards;
    }

    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.7; }
    }

    @keyframes glow {
        0%, 100% { box-shadow: 0 0 20px rgba(0, 196, 154, 0.2); }
        50% { box-shadow: 0 0 40px rgba(0, 196, 154, 0.4); }
    }

    /* Stat cards with glow */
    .stat-card {
        background: linear-gradient(145deg, #151820 0%, #1c202a 100%);
        border: 1px solid #2a3042;
        padding: 1.5rem;
        text-align: center;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }

    .stat-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(0, 196, 154, 0.1), transparent);
        transition: left 0.5s ease;
    }

    .stat-card:hover::before {
        left: 100%;
    }

    .stat-card:hover {
        border-color: #00C49A;
        transform: translateY(-2px);
        box-shadow: 0 10px 40px rgba(0, 196, 154, 0.15);
    }

    .stat-number {
        font-family: 'JetBrains Mono', monospace;
        font-size: 2.5rem;
        font-weight: 700;
        color: #00C49A;
        margin-bottom: 0.25rem;
        text-shadow: 0 0 30px rgba(0, 196, 154, 0.3);
    }

    .stat-label {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.7rem;
        text-transform: uppercase;
        letter-spacing: 0.15em;
        color: #6b7489;
    }

    .stat-delta {
        font-size: 0.75rem;
        margin-top: 0.5rem;
        padding: 0.2rem 0.5rem;
        display: inline-block;
    }

    .stat-delta-up {
        color: #2ECC71;
        background: rgba(46, 204, 113, 0.1);
    }

    .stat-delta-down {
        color: #FF4D4D;
        background: rgba(255, 77, 77, 0.1);
    }

    /* Memory cards */
    .memory-card {
        background: #151820;
        border: 1px solid #2a3042;
        padding: 1.25rem;
        margin-bottom: 0.75rem;
        transition: all 0.25s ease;
        cursor: pointer;
        position: relative;
    }

    .memory-card:hover {
        border-color: #00C49A;
        background: #1c202a;
        transform: translateX(4px);
    }

    .memory-card::after {
        content: '';
        position: absolute;
        left: 0;
        top: 0;
        bottom: 0;
        width: 3px;
        background: var(--level-color, #00C49A);
        opacity: 0;
        transition: opacity 0.25s ease;
    }

    .memory-card:hover::after {
        opacity: 1;
    }

    .memory-content {
        color: #e2e4e9;
        font-size: 0.95rem;
        line-height: 1.5;
        margin-bottom: 0.75rem;
    }

    .memory-meta {
        display: flex;
        justify-content: space-between;
        align-items: center;
        color: #6b7489;
        font-size: 0.7rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    .memory-type {
        padding: 0.15rem 0.5rem;
        border: 1px solid currentColor;
        opacity: 0.8;
    }

    .memory-salience {
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    .salience-bar {
        width: 60px;
        height: 4px;
        background: #2a3042;
        position: relative;
    }

    .salience-fill {
        position: absolute;
        left: 0;
        top: 0;
        height: 100%;
        background: linear-gradient(90deg, #00C49A, #2ECC71);
    }

    /* Level colors */
    .level-1 { --level-color: #FF4D4D; }
    .level-2 { --level-color: #D97757; }
    .level-3 { --level-color: #3399FF; }
    .level-4 { --level-color: #9D8CFF; }

    /* Search section - custom styled */
    .search-section {
        background: linear-gradient(145deg, #151820 0%, #1a1e28 100%);
        border: 1px solid #2a3042;
        padding: 1.5rem 2rem;
        margin: 2rem 0;
        position: relative;
        overflow: hidden;
    }

    .search-section::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 1px;
        background: linear-gradient(90deg, transparent, #00C49A, transparent);
        opacity: 0.5;
    }

    .search-label {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.7rem;
        text-transform: uppercase;
        letter-spacing: 0.15em;
        color: #00C49A;
        margin-bottom: 0.75rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    .search-label-icon {
        width: 16px;
        height: 16px;
        border: 1px solid #00C49A;
        position: relative;
    }

    .search-label-icon::after {
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        width: 6px;
        height: 6px;
        background: #00C49A;
        transform: translate(-50%, -50%);
    }

    /* Force sharp corners on ALL inputs */
    input, .stTextInput input, .stTextInput > div > div > input,
    [data-baseweb="input"] input,
    [data-baseweb="base-input"] input,
    .stTextInput [data-baseweb="input"],
    .stTextInput [data-baseweb="base-input"],
    .stTextInput > div > div,
    .stTextInput > div,
    [data-baseweb="input"],
    [data-baseweb="base-input"],
    .stTextInput * {
        border-radius: 0 !important;
        -webkit-border-radius: 0 !important;
        -moz-border-radius: 0 !important;
    }

    .stTextInput input {
        background: #0e1016 !important;
        border: 1px solid #2a3042 !important;
        color: #e2e4e9 !important;
        font-family: 'JetBrains Mono', monospace !important;
        padding: 0.75rem 1rem !important;
        font-size: 0.9rem !important;
    }

    .stTextInput input:focus {
        border-color: #00C49A !important;
        box-shadow: 0 0 20px rgba(0, 196, 154, 0.2) !important;
        outline: none !important;
    }

    .stTextInput input::placeholder {
        color: #4a5568 !important;
    }

    /* Mind loading animation */
    .mind-loader {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 4rem 2rem;
        text-align: center;
    }

    .mind-loader-visual {
        position: relative;
        width: 120px;
        height: 120px;
        margin-bottom: 2rem;
    }

    .mind-core {
        position: absolute;
        top: 50%;
        left: 50%;
        width: 20px;
        height: 20px;
        background: #00C49A;
        transform: translate(-50%, -50%);
        animation: corePulse 2s ease-in-out infinite;
    }

    .mind-ring {
        position: absolute;
        top: 50%;
        left: 50%;
        border: 1px solid #00C49A;
        transform: translate(-50%, -50%);
        animation: ringExpand 2s ease-out infinite;
    }

    .mind-ring:nth-child(1) { animation-delay: 0s; }
    .mind-ring:nth-child(2) { animation-delay: 0.4s; }
    .mind-ring:nth-child(3) { animation-delay: 0.8s; }

    .mind-node {
        position: absolute;
        width: 8px;
        height: 8px;
        background: #00C49A;
        animation: nodeFloat 3s ease-in-out infinite;
    }

    .mind-node:nth-child(4) { top: 10%; left: 20%; animation-delay: 0s; }
    .mind-node:nth-child(5) { top: 15%; right: 25%; animation-delay: 0.5s; }
    .mind-node:nth-child(6) { bottom: 20%; left: 15%; animation-delay: 1s; }
    .mind-node:nth-child(7) { bottom: 10%; right: 20%; animation-delay: 1.5s; }
    .mind-node:nth-child(8) { top: 50%; left: 5%; animation-delay: 0.3s; }
    .mind-node:nth-child(9) { top: 50%; right: 5%; animation-delay: 0.8s; }

    .mind-connection {
        position: absolute;
        height: 1px;
        background: linear-gradient(90deg, transparent, #00C49A, transparent);
        transform-origin: left center;
        animation: connectionPulse 2s ease-in-out infinite;
    }

    @keyframes corePulse {
        0%, 100% { transform: translate(-50%, -50%) scale(1); opacity: 1; }
        50% { transform: translate(-50%, -50%) scale(1.2); opacity: 0.8; }
    }

    @keyframes ringExpand {
        0% { width: 20px; height: 20px; opacity: 1; }
        100% { width: 100px; height: 100px; opacity: 0; }
    }

    @keyframes nodeFloat {
        0%, 100% { transform: translateY(0) scale(1); opacity: 0.6; }
        50% { transform: translateY(-5px) scale(1.2); opacity: 1; }
    }

    @keyframes connectionPulse {
        0%, 100% { opacity: 0.3; }
        50% { opacity: 0.8; }
    }

    .mind-loader-text {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.85rem;
        color: #6b7489;
        margin-bottom: 0.5rem;
    }

    .mind-loader-subtext {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.7rem;
        color: #00C49A;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        animation: textPulse 1.5s ease-in-out infinite;
    }

    @keyframes textPulse {
        0%, 100% { opacity: 0.5; }
        50% { opacity: 1; }
    }

    /* Settings Panel */
    .settings-section {
        margin-bottom: 1.5rem;
    }

    .settings-title {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.7rem;
        text-transform: uppercase;
        letter-spacing: 0.15em;
        color: #00C49A;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    .sensitivity-option {
        background: #151820;
        border: 1px solid #2a3042;
        padding: 1rem;
        margin-bottom: 0.5rem;
        cursor: pointer;
        transition: all 0.2s ease;
        position: relative;
    }

    .sensitivity-option:hover {
        border-color: #3d4558;
        background: #1a1e28;
    }

    .sensitivity-option.selected {
        border-color: #00C49A;
        background: linear-gradient(145deg, #151820 0%, #1a2520 100%);
    }

    .sensitivity-option.selected::before {
        content: '';
        position: absolute;
        left: 0;
        top: 0;
        bottom: 0;
        width: 3px;
        background: #00C49A;
    }

    .sensitivity-header {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        margin-bottom: 0.5rem;
    }

    .sensitivity-icon {
        font-size: 1.25rem;
        width: 28px;
        text-align: center;
    }

    .sensitivity-name {
        font-size: 0.95rem;
        font-weight: 500;
        color: #e2e4e9;
    }

    .sensitivity-tag {
        font-size: 0.65rem;
        padding: 0.15rem 0.4rem;
        background: rgba(0, 196, 154, 0.15);
        color: #00C49A;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-left: auto;
    }

    .sensitivity-desc {
        font-size: 0.8rem;
        color: #9aa3b5;
        line-height: 1.5;
        margin-bottom: 0.75rem;
        padding-left: 2.75rem;
    }

    .sensitivity-examples {
        padding-left: 2.75rem;
    }

    .sensitivity-example {
        font-size: 0.7rem;
        color: #6b7489;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        margin-bottom: 0.25rem;
    }

    .sensitivity-example::before {
        content: '→';
        color: #00C49A;
    }

    .sensitivity-bar {
        display: flex;
        gap: 3px;
        margin-top: 0.75rem;
        padding-left: 2.75rem;
    }

    .sensitivity-bar-segment {
        height: 4px;
        flex: 1;
        background: #2a3042;
    }

    .sensitivity-bar-segment.filled {
        background: #00C49A;
    }

    /* Memory levels - full width cards */
    .level-card {
        background: linear-gradient(145deg, #151820 0%, #1c202a 100%);
        border: 1px solid #2a3042;
        padding: 1.25rem;
        margin-bottom: 0.75rem;
        display: flex;
        align-items: center;
        gap: 1rem;
        transition: all 0.25s ease;
    }

    .level-card:hover {
        border-color: var(--level-color);
        transform: translateX(4px);
    }

    .level-icon {
        font-size: 2rem;
        width: 50px;
        text-align: center;
    }

    .level-info {
        flex: 1;
    }

    .level-name {
        color: #e2e4e9;
        font-size: 1rem;
        font-weight: 500;
        margin-bottom: 0.25rem;
    }

    .level-duration {
        color: var(--level-color);
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.1em;
    }

    .level-desc {
        color: #6b7489;
        font-size: 0.8rem;
        margin-top: 0.25rem;
    }

    .level-count {
        font-size: 1.5rem;
        font-weight: 600;
        color: var(--level-color);
        min-width: 40px;
        text-align: right;
    }

    /* Insight card */
    .insight-card {
        background: linear-gradient(135deg, rgba(0, 196, 154, 0.1) 0%, rgba(157, 140, 255, 0.1) 100%);
        border: 1px solid rgba(0, 196, 154, 0.3);
        padding: 1.5rem;
        margin: 1rem 0;
    }

    .insight-title {
        color: #00C49A;
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-bottom: 0.75rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    .insight-content {
        color: #e2e4e9;
        font-size: 1rem;
        line-height: 1.6;
    }

    /* Empty state */
    .empty-state {
        text-align: center;
        padding: 4rem 2rem;
        color: #6b7489;
    }

    .empty-state-icon {
        font-size: 4rem;
        margin-bottom: 1rem;
        opacity: 0.5;
    }

    /* Timeline */
    .timeline-container {
        position: relative;
        padding-left: 2rem;
    }

    .timeline-line {
        position: absolute;
        left: 0.5rem;
        top: 0;
        bottom: 0;
        width: 2px;
        background: linear-gradient(180deg, #00C49A, #2a3042);
    }

    .timeline-item {
        position: relative;
        margin-bottom: 1.5rem;
    }

    .timeline-dot {
        position: absolute;
        left: -1.75rem;
        top: 0.5rem;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        background: #00C49A;
        box-shadow: 0 0 10px rgba(0, 196, 154, 0.5);
    }

    /* Keyboard shortcut hints */
    .kbd {
        background: #2a3042;
        border: 1px solid #3d4558;
        padding: 0.1rem 0.4rem;
        font-size: 0.7rem;
        color: #9aa3b5;
        font-family: 'JetBrains Mono', monospace;
    }

    /* Section headers */
    .section-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin: 2rem 0 1rem 0;
        padding-bottom: 0.75rem;
        border-bottom: 1px solid #2a3042;
    }

    .section-title {
        font-family: 'Instrument Serif', Georgia, serif;
        font-size: 1.5rem;
        color: #e2e4e9;
    }

    .section-action {
        color: #00C49A;
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        cursor: pointer;
    }

    .section-action:hover {
        text-decoration: underline;
    }

    /* Settings Section */
    .settings-section {
        background: linear-gradient(145deg, #151820 0%, #1c202a 100%);
        border: 1px solid #2a3042;
        padding: 2rem;
        margin-top: 2rem;
    }

    .settings-header {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        margin-bottom: 1.5rem;
        padding-bottom: 1rem;
        border-bottom: 1px solid #2a3042;
    }

    .settings-icon {
        font-size: 1.5rem;
    }

    .settings-title {
        font-family: 'Instrument Serif', Georgia, serif;
        font-size: 1.5rem;
        color: #e2e4e9;
    }

    .settings-subtitle {
        font-size: 0.8rem;
        color: #6b7489;
        margin-left: auto;
    }

    /* Sensitivity Grid */
    .sensitivity-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 1rem;
    }

    @media (max-width: 1200px) {
        .sensitivity-grid {
            grid-template-columns: repeat(2, 1fr);
        }
    }

    @media (max-width: 768px) {
        .sensitivity-grid {
            grid-template-columns: 1fr;
        }
    }

    .sens-card {
        background: #0e1016;
        border: 2px solid #2a3042;
        padding: 1.25rem;
        cursor: pointer;
        transition: all 0.25s ease;
        position: relative;
    }

    .sens-card:hover {
        border-color: #3d4558;
        transform: translateY(-2px);
    }

    .sens-card.active {
        border-color: #00C49A;
        background: rgba(0, 196, 154, 0.05);
    }

    .sens-card.active::after {
        content: '✓';
        position: absolute;
        top: 0.75rem;
        right: 0.75rem;
        color: #00C49A;
        font-size: 1rem;
    }

    .sens-card-header {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        margin-bottom: 0.75rem;
    }

    .sens-card-icon {
        font-size: 1.25rem;
    }

    .sens-card-name {
        font-weight: 600;
        color: #e2e4e9;
        font-size: 1rem;
    }

    .sens-card-tag {
        background: rgba(0, 196, 154, 0.15);
        color: #00C49A;
        font-size: 0.6rem;
        padding: 0.15rem 0.4rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-left: auto;
    }

    .sens-card-desc {
        color: #9aa3b5;
        font-size: 0.8rem;
        line-height: 1.5;
        margin-bottom: 1rem;
    }

    .sens-card-examples {
        border-top: 1px solid #2a3042;
        padding-top: 0.75rem;
    }

    .sens-card-example {
        font-size: 0.7rem;
        color: #6b7489;
        font-family: 'JetBrains Mono', monospace;
        margin-bottom: 0.35rem;
    }

    .sens-card-example:last-child {
        margin-bottom: 0;
    }

    .sens-level-bar {
        display: flex;
        gap: 0.25rem;
        margin-top: 1rem;
    }

    .sens-level-segment {
        height: 4px;
        flex: 1;
        background: #2a3042;
    }

    .sens-level-segment.filled {
        background: #00C49A;
    }
</style>
"""

st.markdown(USER_CSS, unsafe_allow_html=True)


def get_api_client():
    """Get HTTP client for API calls."""
    return httpx.Client(base_url=API_BASE, timeout=30.0)


@st.cache_data(ttl=30)  # Cache for 30 seconds to speed up page loads
def fetch_all_memories(user_id: str) -> list:
    """Fetch all memories for a user (cached)."""
    try:
        with get_api_client() as client:
            # Use new list endpoint - doesn't require embeddings
            resp = client.get(
                "/v1/memories/",
                params={"user_id": user_id, "limit": 100},
            )
            if resp.status_code == 200:
                memories = resp.json()
                memories.sort(key=lambda x: x.get("created_at", ""), reverse=True)
                return memories
    except Exception as e:
        st.error(f"API Error: {e}")

    return []


def fetch_user_stats(user_id: str, query: str = "") -> dict:
    """Fetch user statistics from the API."""
    # Get cached memories
    memories = fetch_all_memories(user_id)

    # Filter by query if provided
    if query:
        query_lower = query.lower()
        memories = [m for m in memories if query_lower in m.get("content", "").lower()]

    return {
        "total_memories": len(memories),
        "memories": memories,
        "by_level": count_by_level(memories),
    }


def count_by_level(memories: list) -> dict:
    """Count memories by temporal level."""
    counts = {1: 0, 2: 0, 3: 0, 4: 0}
    for m in memories:
        level = m.get("temporal_level", 2)
        counts[level] = counts.get(level, 0) + 1
    return counts


def render_mind_loader():
    """Render mind-themed loading animation."""
    st.markdown(
        """
        <div class="mind-loader">
            <div class="mind-loader-visual">
                <div class="mind-ring"></div>
                <div class="mind-ring"></div>
                <div class="mind-ring"></div>
                <div class="mind-node"></div>
                <div class="mind-node"></div>
                <div class="mind-node"></div>
                <div class="mind-node"></div>
                <div class="mind-node"></div>
                <div class="mind-node"></div>
                <div class="mind-core"></div>
            </div>
            <div class="mind-loader-text">Gathering your memories...</div>
            <div class="mind-loader-subtext">Connecting neural pathways</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_search_section():
    """Render the search section with proper VIBESHIP styling."""
    st.markdown(
        """
        <div class="search-section">
            <div class="search-label">
                <div class="search-label-icon"></div>
                Search Your Mind
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# Memory sensitivity configuration
SENSITIVITY_OPTIONS = [
    {
        "id": "minimal",
        "name": "Minimal",
        "icon": "🎯",
        "tag": "Recommended",
        "description": "Only remembers what truly defines you. Core preferences, skills, and traits that shape who you are.",
        "examples": [
            '"I\'m a Python developer" → Saved',
            '"I prefer dark mode" → Saved',
            '"Working on a bug fix" → Not saved',
        ],
        "bars": 1,
    },
    {
        "id": "balanced",
        "name": "Balanced",
        "icon": "⚖️",
        "tag": "",
        "description": "Remembers important context plus your preferences. Good balance between memory and noise.",
        "examples": [
            '"I\'m debugging the auth flow" → Saved',
            '"Using React for this project" → Saved',
            '"Let me think about this" → Not saved',
        ],
        "bars": 2,
    },
    {
        "id": "detailed",
        "name": "Detailed",
        "icon": "📝",
        "tag": "",
        "description": "Captures most useful information from your conversations. More context for better assistance.",
        "examples": [
            '"The API returns 404 errors" → Saved',
            '"Meeting with team tomorrow" → Saved',
            '"Hmm, interesting" → Not saved',
        ],
        "bars": 3,
    },
    {
        "id": "everything",
        "name": "Everything",
        "icon": "🧠",
        "tag": "",
        "description": "Remembers as much as possible. Maximum context retention for comprehensive memory.",
        "examples": [
            '"Trying a new approach" → Saved',
            '"This is frustrating" → Saved',
            '"Only greetings ignored" → Not saved',
        ],
        "bars": 4,
    },
]


def save_user_preference(user_id: str, sensitivity: str) -> bool:
    """Save user's memory sensitivity preference."""
    try:
        with get_api_client() as client:
            resp = client.post(
                "/v1/users/preferences",
                json={"user_id": user_id, "memory_sensitivity": sensitivity},
            )
            return resp.status_code == 200
    except Exception:
        return False


def get_user_preference(user_id: str) -> str:
    """Get user's memory sensitivity preference."""
    try:
        with get_api_client() as client:
            resp = client.get(f"/v1/users/preferences/{user_id}")
            if resp.status_code == 200:
                return resp.json().get("memory_sensitivity", "minimal")
    except Exception:
        pass
    return "minimal"  # Default


def render_settings_section(current_sensitivity: str) -> str | None:
    """Render the settings section with memory sensitivity selector."""
    options = {opt["id"]: opt for opt in SENSITIVITY_OPTIONS}

    # Clean section header using VIBESHIP style
    st.markdown(
        """
        <div class="section-header" style="margin-top: 3rem;">
            <div class="section-title">Memory Settings</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Simple select box instead of cluttered radio buttons
    option_names = [f"{opt['name']}" for opt in SENSITIVITY_OPTIONS]
    current_index = next(
        (i for i, opt in enumerate(SENSITIVITY_OPTIONS) if opt["id"] == current_sensitivity),
        0,
    )

    selected_index = st.selectbox(
        "How much should Mind remember?",
        range(len(option_names)),
        index=current_index,
        format_func=lambda i: option_names[i],
        label_visibility="visible",
    )

    selected_opt = SENSITIVITY_OPTIONS[selected_index]
    selected_id = selected_opt["id"]

    # Show description in a clean card
    bars_html = "".join(
        f'<div style="width: 20px; height: 4px; background: {"#00C49A" if i < selected_opt["bars"] else "#2a3042"};"></div>'
        for i in range(4)
    )

    st.markdown(
        f"""
        <div style="background: #151820; border: 1px solid #2a3042; padding: 1.25rem; margin-top: 1rem;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem;">
                <span style="color: #e2e4e9; font-weight: 500;">{selected_opt['name']}</span>
                <div style="display: flex; gap: 4px;">{bars_html}</div>
            </div>
            <p style="color: #9aa3b5; font-size: 0.875rem; margin: 0; line-height: 1.5;">
                {selected_opt['description']}
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Return new selection if changed
    if selected_id != current_sensitivity:
        return selected_id
    return None


def render_hero(user_id: str):
    """Render the hero section with welcome message."""
    st.markdown(
        """
        <div class="hero-container">
            <div class="hero-title">Your Mind</div>
            <div class="hero-subtitle">Explore your memories and see your story unfold</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_stats(stats: dict):
    """Render the stats section with animated cards."""
    col1, col2, col3, col4 = st.columns(4)

    total = stats.get("total_memories", 0)
    by_level = stats.get("by_level", {})

    with col1:
        st.markdown(
            f"""
            <div class="stat-card">
                <div class="stat-number">{total}</div>
                <div class="stat-label">Total Memories</div>
                <div class="stat-delta stat-delta-up">+3 this week</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        identity_count = by_level.get(4, 0)
        st.markdown(
            f"""
            <div class="stat-card">
                <div class="stat-number">{identity_count}</div>
                <div class="stat-label">Identity Memories</div>
                <div class="stat-delta stat-delta-up">Core traits</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col3:
        # Calculate a "mind score" based on memory quality
        mind_score = min(100, total * 2 + identity_count * 5)
        st.markdown(
            f"""
            <div class="stat-card">
                <div class="stat-number">{mind_score}</div>
                <div class="stat-label">Mind Score</div>
                <div class="stat-delta stat-delta-up">Growing</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col4:
        # Decision quality (mock for now)
        quality = 87
        st.markdown(
            f"""
            <div class="stat-card">
                <div class="stat-number">{quality}%</div>
                <div class="stat-label">Decision Quality</div>
                <div class="stat-delta stat-delta-up">+2.3%</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_insight(memories: list):
    """Render an AI-generated insight about the user's memories."""
    if not memories:
        return

    # Pick a random insight type
    insights = [
        ("Pattern Detected", "You seem to prefer typed languages and thorough testing. This suggests you value code reliability and maintainability."),
        ("Memory of the Day", f"'{memories[0].get('content', '')[:100]}...' - stored as a core part of who you are."),
        ("Growth Insight", f"You've built {len(memories)} memories. Your Mind is learning and growing with every interaction."),
    ]

    insight = random.choice(insights)

    st.markdown(
        f"""
        <div class="insight-card">
            <div class="insight-title">
                <span>✨</span>
                {insight[0]}
            </div>
            <div class="insight-content">
                {insight[1]}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_memory_card(memory: dict, index: int):
    """Render a single memory card."""
    content = memory.get("content", "")
    level = memory.get("temporal_level", 2)
    level_name = memory.get("temporal_level_name", "situational")
    content_type = memory.get("content_type", "observation")
    salience = memory.get("effective_salience", 0.5)
    created = memory.get("created_at", "")

    level_colors = {
        1: "#FF4D4D",
        2: "#D97757",
        3: "#3399FF",
        4: "#9D8CFF",
    }
    color = level_colors.get(level, "#00C49A")

    # Format date
    try:
        dt = datetime.fromisoformat(created.replace("Z", "+00:00"))
        date_str = dt.strftime("%b %d, %Y")
    except Exception:
        date_str = "Recently"

    salience_pct = int(salience * 100)

    st.markdown(
        f"""
        <div class="memory-card level-{level}" style="--level-color: {color}; animation: fadeInUp 0.5s ease-out {index * 0.1}s backwards;">
            <div class="memory-content">{content}</div>
            <div class="memory-meta">
                <div style="display: flex; gap: 1rem; align-items: center;">
                    <span class="memory-type" style="color: {color}; border-color: {color};">{level_name}</span>
                    <span style="color: #9aa3b5;">{content_type}</span>
                    <span>{date_str}</span>
                </div>
                <div class="memory-salience">
                    <span>Salience</span>
                    <div class="salience-bar">
                        <div class="salience-fill" style="width: {salience_pct}%;"></div>
                    </div>
                    <span style="color: #00C49A;">{salience_pct}%</span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_memory_stream(memories: list):
    """Render the memory stream."""
    st.markdown(
        """
        <div class="section-header">
            <div class="section-title">Memory Stream</div>
            <div class="section-action">View all</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not memories:
        st.markdown(
            """
            <div class="mind-loader">
                <div class="mind-loader-visual">
                    <div class="mind-ring"></div>
                    <div class="mind-ring"></div>
                    <div class="mind-ring"></div>
                    <div class="mind-node"></div>
                    <div class="mind-node"></div>
                    <div class="mind-node"></div>
                    <div class="mind-node"></div>
                    <div class="mind-node"></div>
                    <div class="mind-node"></div>
                    <div class="mind-core"></div>
                </div>
                <div class="mind-loader-text">No memories found</div>
                <div class="mind-loader-subtext">Start a conversation to build your Mind</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    # Show memories (already filtered by fetch_user_stats)
    for i, memory in enumerate(memories[:10]):
        render_memory_card(memory, i)

    if len(memories) > 10:
        st.markdown(
            f"""
            <div style="text-align: center; margin: 1.5rem 0; color: #6b7489;">
                Showing 10 of {len(memories)} memories
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_memory_distribution(by_level: dict):
    """Render memory distribution as clean horizontal bars."""
    total = sum(by_level.values()) if by_level else 0

    st.markdown(
        f"""
        <div class="section-header">
            <div class="section-title">Distribution</div>
        </div>
        <div style="text-align: center; margin-bottom: 1.5rem;">
            <div style="font-size: 3rem; font-weight: 700; color: #00C49A; text-shadow: 0 0 30px rgba(0, 196, 154, 0.3);">{total}</div>
            <div style="font-size: 0.75rem; color: #6b7489; text-transform: uppercase; letter-spacing: 0.1em;">Total Memories</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    levels = [
        ("Identity", 4, "#9D8CFF", "Core traits"),
        ("Seasonal", 3, "#3399FF", "Patterns"),
        ("Situational", 2, "#D97757", "Recent"),
        ("Immediate", 1, "#FF4D4D", "Now"),
    ]

    for name, level_num, color, desc in levels:
        count = by_level.get(level_num, 0)
        pct = (count / total * 100) if total > 0 else 0

        st.markdown(
            f"""
            <div style="margin-bottom: 1rem;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.25rem;">
                    <span style="color: #e2e4e9; font-size: 0.85rem;">{name}</span>
                    <span style="color: {color}; font-weight: 600;">{count}</span>
                </div>
                <div style="height: 8px; background: #1c202a; position: relative;">
                    <div style="position: absolute; left: 0; top: 0; height: 100%; width: {pct}%; background: {color}; transition: width 0.5s ease;"></div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_level_legend(by_level: dict):
    """Render memory levels as full-width cards with counts."""
    levels = [
        ("🟣", "Identity", "Years", "Core preferences & traits", 4, "#9D8CFF"),
        ("🔵", "Seasonal", "Months", "Recurring patterns", 3, "#3399FF"),
        ("🟠", "Situational", "Days-Weeks", "Recent projects", 2, "#D97757"),
        ("🔴", "Immediate", "Hours", "Current context", 1, "#FF4D4D"),
    ]

    st.markdown(
        """
        <div class="section-header">
            <div class="section-title">Memory Levels</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    for icon, name, duration, desc, level_num, color in levels:
        count = by_level.get(level_num, 0)
        st.markdown(
            f"""
            <div class="level-card level-{level_num}" style="--level-color: {color};">
                <div class="level-icon">{icon}</div>
                <div class="level-info">
                    <div class="level-name">{name}</div>
                    <div class="level-duration">{duration}</div>
                    <div class="level-desc">{desc}</div>
                </div>
                <div class="level-count">{count}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def main():
    """Main app entry point."""
    # Always use the correct user ID
    st.session_state.user_id = DEFAULT_USER_ID

    # Initialize sensitivity in session state (load from API on first run)
    if "memory_sensitivity" not in st.session_state:
        st.session_state.memory_sensitivity = get_user_preference(st.session_state.user_id)

    # Render hero first
    render_hero(st.session_state.user_id)

    # Search section with proper styling - label above input
    st.markdown(
        """
        <div class="search-label" style="margin-top: 1rem;">
            <div class="search-label-icon"></div>
            Search Your Mind
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Search input
    query = st.text_input(
        "Search",
        placeholder="Type to search your memories...",
        label_visibility="collapsed",
        key="search_query",
    )

    # Fetch data (cached for speed)
    stats = fetch_user_stats(st.session_state.user_id, query if query else "")
    render_stats(stats)

    # Insight
    render_insight(stats.get("memories", []))

    # Two column layout: Memories on left, Chart on right
    col1, col2 = st.columns([3, 2])

    with col1:
        render_memory_stream(stats.get("memories", []))

    with col2:
        render_memory_distribution(stats.get("by_level", {}))

    # Memory levels - full width below
    st.markdown("<br>", unsafe_allow_html=True)
    render_level_legend(stats.get("by_level", {}))

    # Settings section
    new_sensitivity = render_settings_section(st.session_state.memory_sensitivity)
    if new_sensitivity:
        st.session_state.memory_sensitivity = new_sensitivity
        save_user_preference(st.session_state.user_id, new_sensitivity)
        st.rerun()

    # Footer
    st.markdown(
        """
        <div style="text-align: center; margin-top: 3rem; padding: 1.5rem; border-top: 1px solid #2a3042; color: #6b7489; font-size: 0.75rem;">
            <span style="color: #00C49A;">Mind v5</span> · Your memories, your story ·
            <span style="font-family: 'Instrument Serif', Georgia, serif;">VIBESHIP</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()

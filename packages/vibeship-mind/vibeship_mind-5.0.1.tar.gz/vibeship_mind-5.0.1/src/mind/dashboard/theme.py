"""VIBESHIP Theme Configuration.

Authentic VIBESHIP design system:
- Bluish-black backgrounds
- Sharp corners (NO border-radius)
- Green-dim (#00C49A) as primary accent
- JetBrains Mono for body/buttons
- Instrument Serif for headings
- Terminal-inspired aesthetic
"""

# VIBESHIP Color Palette (from web/src/lib/styles/theme.css)
COLORS = {
    # Backgrounds - Bluish black tones (Dark Mode)
    "bg_primary": "#0e1016",
    "bg_secondary": "#151820",
    "bg_tertiary": "#1c202a",
    "bg_inverse": "#ffffff",
    # Text
    "text_primary": "#e2e4e9",
    "text_secondary": "#9aa3b5",
    "text_tertiary": "#6b7489",
    "text_inverse": "#0c0e14",
    # Borders
    "border": "#2a3042",
    "border_strong": "#3d4558",
    # Accent Colors - VIBESHIP Palette
    "green": "#2ECC71",  # Terminal Green - success
    "green_dim": "#00C49A",  # PRIMARY ACCENT - use this most
    "orange": "#D97757",  # Claude Coral - warning (not FFB020)
    "red": "#FF4D4D",  # Debug Red - error/critical
    "blue": "#3399FF",  # Docker Blue - info
    "violet": "#9D8CFF",  # Syntax Violet - analytics
    "pink": "#FF66C4",  # Hot Pink - high priority
    # Grays - Bluish tints
    "gray_100": "#0f1218",
    "gray_200": "#181c25",
    "gray_300": "#2a3142",
    "gray_400": "#3d4559",
    "gray_500": "#5a6478",
    "gray_600": "#8892a6",
    "gray_700": "#b8c0d0",
    "gray_800": "#dce1eb",
}

# Custom CSS for authentic VIBESHIP styling
CUSTOM_CSS = """
<style>
    /* Import VIBESHIP Fonts - JetBrains Mono (body) + Instrument Serif (headings) */
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&family=Instrument+Serif:ital@0;1&display=swap');

    /* CSS Variables - Exact VIBESHIP values */
    :root {
        /* Backgrounds */
        --bg-primary: #0e1016;
        --bg-secondary: #151820;
        --bg-tertiary: #1c202a;

        /* Text */
        --text-primary: #e2e4e9;
        --text-secondary: #9aa3b5;
        --text-tertiary: #6b7489;

        /* Borders */
        --border: #2a3042;
        --border-strong: #3d4558;

        /* Accents */
        --green: #2ECC71;
        --green-dim: #00C49A;
        --orange: #D97757;
        --red: #FF4D4D;
        --blue: #3399FF;
        --violet: #9D8CFF;
        --pink: #FF66C4;

        /* Fonts */
        --font-mono: 'JetBrains Mono', 'SF Mono', 'Fira Code', monospace;
        --font-serif: 'Instrument Serif', Georgia, serif;

        /* Spacing */
        --space-1: 0.25rem;
        --space-2: 0.5rem;
        --space-3: 0.75rem;
        --space-4: 1rem;
        --space-5: 1.25rem;
        --space-6: 1.5rem;

        /* Transitions */
        --transition-fast: 0.15s ease;
    }

    /* Main app - Bluish black */
    .stApp {
        background: var(--bg-primary) !important;
    }

    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Global text styling - JetBrains Mono */
    .stApp, .stApp p, .stApp span, .stApp div, .stApp label {
        font-family: var(--font-mono) !important;
        color: var(--text-primary);
    }

    /* VIBESHIP Header - Instrument Serif */
    .vibeship-header {
        font-family: var(--font-serif) !important;
        font-size: 2.5rem;
        font-weight: 400;
        color: var(--text-primary);
        margin-bottom: 0.25rem;
        letter-spacing: -0.02em;
    }

    .vibeship-subtitle {
        font-family: var(--font-mono);
        color: var(--text-secondary);
        font-size: 0.875rem;
        margin-bottom: 2rem;
    }

    /* Metric Cards - Sharp corners, 1px border */
    .metric-card {
        background: var(--bg-secondary);
        border: 1px solid var(--border);
        padding: var(--space-5);
        transition: border-color var(--transition-fast);
    }

    .metric-card:hover {
        border-color: var(--green-dim);
    }

    .metric-value {
        font-size: 1.75rem;
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: 0.25rem;
        font-family: var(--font-mono);
    }

    .metric-label {
        font-size: 0.7rem;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: var(--text-secondary);
        margin-bottom: 0.5rem;
        font-weight: 500;
    }

    .metric-delta-positive {
        font-size: 0.75rem;
        color: var(--green);
    }

    .metric-delta-negative {
        font-size: 0.75rem;
        color: var(--red);
    }

    /* Status badges */
    .status-healthy {
        color: var(--green);
        font-family: var(--font-mono);
        font-size: 0.75rem;
    }

    .status-unhealthy {
        color: var(--red);
        font-family: var(--font-mono);
        font-size: 0.75rem;
    }

    /* Memory level badges - Sharp corners */
    .level-immediate {
        background: rgba(255, 77, 77, 0.15);
        color: #FF6B6B;
        border: 1px solid rgba(255, 77, 77, 0.3);
        padding: 0.2rem 0.5rem;
        font-size: 0.65rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        font-family: var(--font-mono);
    }

    .level-situational {
        background: rgba(217, 119, 87, 0.15);
        color: #D97757;
        border: 1px solid rgba(217, 119, 87, 0.3);
        padding: 0.2rem 0.5rem;
        font-size: 0.65rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        font-family: var(--font-mono);
    }

    .level-seasonal {
        background: rgba(51, 153, 255, 0.15);
        color: #3399FF;
        border: 1px solid rgba(51, 153, 255, 0.3);
        padding: 0.2rem 0.5rem;
        font-size: 0.65rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        font-family: var(--font-mono);
    }

    .level-identity {
        background: rgba(157, 140, 255, 0.15);
        color: #9D8CFF;
        border: 1px solid rgba(157, 140, 255, 0.3);
        padding: 0.2rem 0.5rem;
        font-size: 0.65rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        font-family: var(--font-mono);
    }

    /* Sidebar - VIBESHIP style */
    [data-testid="stSidebar"] {
        background: var(--bg-secondary) !important;
        border-right: 1px solid var(--border) !important;
    }

    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
        color: var(--text-secondary);
        font-family: var(--font-mono);
    }

    /* Radio buttons in sidebar */
    [data-testid="stSidebar"] .stRadio > label {
        color: var(--text-secondary) !important;
        font-size: 0.85rem;
        font-family: var(--font-mono);
    }

    [data-testid="stSidebar"] .stRadio > div {
        gap: 0.25rem;
    }

    [data-testid="stSidebar"] .stRadio > div > label {
        padding: 0.6rem 1rem;
        border: 1px solid transparent;
        transition: all var(--transition-fast);
    }

    [data-testid="stSidebar"] .stRadio > div > label:hover {
        border-color: var(--border);
        background: var(--bg-tertiary);
    }

    [data-testid="stSidebar"] .stRadio > div > label[data-checked="true"] {
        background: var(--bg-tertiary);
        border-color: var(--green-dim);
        color: var(--text-primary) !important;
    }

    /* Buttons - VIBESHIP outline style with SHARP CORNERS */
    .stButton > button {
        background: transparent !important;
        border: 1px solid var(--green-dim) !important;
        color: var(--green-dim) !important;
        border-radius: 0 !important;  /* SHARP CORNERS */
        font-family: var(--font-mono) !important;
        font-size: 0.8rem !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        padding: 0.75rem 1.25rem !important;
        transition: all var(--transition-fast) !important;
        font-weight: 500;
    }

    .stButton > button:hover {
        background: var(--green-dim) !important;
        color: var(--bg-primary) !important;
        box-shadow: 0 0 20px rgba(0, 196, 154, 0.3);
    }

    /* Text inputs - Sharp corners */
    .stTextInput > div > div > input {
        background: var(--bg-primary) !important;
        border: 1px solid var(--border) !important;
        border-radius: 0 !important;  /* SHARP CORNERS */
        color: var(--text-primary) !important;
        font-family: var(--font-mono) !important;
    }

    .stTextInput > div > div > input:focus {
        border-color: var(--green-dim) !important;
        box-shadow: none !important;
    }

    .stTextInput > div > div > input::placeholder {
        color: var(--text-tertiary) !important;
    }

    /* Labels */
    .stTextInput > label, .stSlider > label, .stSelectbox > label {
        font-family: var(--font-mono) !important;
        color: var(--text-secondary) !important;
        font-size: 0.8rem !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    /* Sliders */
    .stSlider > div > div > div {
        background: var(--border) !important;
    }

    .stSlider > div > div > div > div {
        background: var(--green-dim) !important;
    }

    /* Tabs - Sharp corners */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0;
        background: transparent;
        border-bottom: 1px solid var(--border);
    }

    .stTabs [data-baseweb="tab"] {
        background: transparent !important;
        border-radius: 0 !important;  /* SHARP CORNERS */
        color: var(--text-secondary) !important;
        border: 1px solid transparent;
        border-bottom: none;
        padding: 0.75rem 1.25rem !important;
        font-family: var(--font-mono);
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    .stTabs [data-baseweb="tab"]:hover {
        color: var(--text-primary) !important;
    }

    .stTabs [aria-selected="true"] {
        background: var(--bg-secondary) !important;
        border-color: var(--border) !important;
        border-bottom-color: var(--bg-secondary) !important;
        color: var(--green-dim) !important;
        margin-bottom: -1px;
    }

    /* Expanders - Sharp corners */
    .streamlit-expanderHeader {
        background: var(--bg-secondary) !important;
        border: 1px solid var(--border) !important;
        border-radius: 0 !important;  /* SHARP CORNERS */
        color: var(--text-primary) !important;
        font-family: var(--font-mono);
        font-size: 0.85rem;
    }

    .streamlit-expanderHeader:hover {
        border-color: var(--green-dim) !important;
    }

    .streamlit-expanderContent {
        background: var(--bg-primary) !important;
        border: 1px solid var(--border) !important;
        border-top: none !important;
        border-radius: 0 !important;  /* SHARP CORNERS */
    }

    /* Success/Info/Warning/Error messages */
    .stSuccess, .stInfo, .stWarning, .stError {
        border-radius: 0 !important;  /* SHARP CORNERS */
        font-family: var(--font-mono);
    }

    /* Code blocks */
    code {
        font-family: var(--font-mono) !important;
        background: var(--bg-tertiary) !important;
        color: var(--green-dim) !important;
        padding: 0.1rem 0.3rem;
        font-size: 0.85em;
        border-radius: 2px !important;  /* Only code gets tiny radius */
    }

    /* Headings in markdown - Instrument Serif */
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        font-family: var(--font-serif) !important;
        font-weight: 400;
        color: var(--text-primary);
    }

    /* Progress bars */
    .stProgress > div > div {
        background: var(--green-dim) !important;
        border-radius: 0 !important;  /* SHARP CORNERS */
    }

    /* Dividers */
    hr {
        border-color: var(--border) !important;
    }

    /* Plotly charts */
    .js-plotly-plot {
        border-radius: 0 !important;
    }

    /* Select boxes - Sharp corners */
    .stSelectbox > div > div {
        background: var(--bg-primary) !important;
        border: 1px solid var(--border) !important;
        border-radius: 0 !important;  /* SHARP CORNERS */
    }

    /* Info boxes */
    .info-box {
        background: var(--bg-secondary);
        border: 1px solid var(--border);
        border-left: 3px solid var(--green-dim);
        padding: 1rem;
        font-size: 0.85rem;
    }

    /* Alert states */
    .warning-box {
        background: rgba(217, 119, 87, 0.1);
        border: 1px solid var(--orange);
        padding: 1rem;
    }

    .error-box {
        background: rgba(255, 77, 77, 0.1);
        border: 1px solid var(--red);
        padding: 1rem;
    }

    .success-box {
        background: rgba(46, 204, 113, 0.1);
        border: 1px solid var(--green);
        padding: 1rem;
    }
</style>
"""

# Plotly chart theme - VIBESHIP style
PLOTLY_THEME = {
    "template": "plotly_dark",
    "layout": {
        "paper_bgcolor": "rgba(14, 16, 22, 0)",
        "plot_bgcolor": "rgba(21, 24, 32, 0.5)",
        "font": {
            "color": "#9aa3b5",
            "family": "JetBrains Mono, monospace",
        },
        # VIBESHIP accent colors
        "colorway": ["#00C49A", "#9D8CFF", "#3399FF", "#FF66C4", "#D97757", "#2ECC71"],
        "xaxis": {
            "gridcolor": "rgba(42, 48, 66, 0.5)",
            "zerolinecolor": "rgba(42, 48, 66, 0.8)",
            "linecolor": "#2a3042",
        },
        "yaxis": {
            "gridcolor": "rgba(42, 48, 66, 0.5)",
            "zerolinecolor": "rgba(42, 48, 66, 0.8)",
            "linecolor": "#2a3042",
        },
    },
}

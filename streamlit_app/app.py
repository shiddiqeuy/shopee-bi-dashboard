"""
Shopee BI Dashboard — Streamlit Application.

Entry point for the Streamlit app. Handles sidebar navigation,
session state initialization, and page routing.
"""

from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

import streamlit as st

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from database.connection import get_connection
from database.repository import DuckDBRepository
from streamlit_app.pages import dashboard_page, upload, settings

st.set_page_config(
    page_title="Shopee BI Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Session state defaults ─────────────────────────────────────────────
_DEFAULTS = {
    "page": "Dashboard",
    "file_hash": None,
    "etl_completed": False,
    "analytics_completed": False,
    "dashboard_generated": False,
    "last_uploaded": None,
    "etl_result": None,
}
for key, value in _DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ── Global CSS ─────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    * { font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important; }

    :root {
        --primary: #2563EB;
        --primary-light: #3B82F6;
        --primary-dark: #1D4ED8;
        --success: #16A34A;
        --warning: #F59E0B;
        --danger: #DC2626;
        --bg: #F8FAFC;
        --surface: #FFFFFF;
        --border: #E2E8F0;
        --text: #0F172A;
        --text-secondary: #64748B;
        --text-muted: #94A3B8;
        --radius: 12px;
        --radius-sm: 8px;
        --shadow: 0 1px 3px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04);
        --shadow-md: 0 4px 6px -1px rgba(0,0,0,0.07), 0 2px 4px -1px rgba(0,0,0,0.04);
        --shadow-lg: 0 10px 15px -3px rgba(0,0,0,0.08), 0 4px 6px -2px rgba(0,0,0,0.04);
    }

    .stApp { background: var(--bg); }
    .main .block-container { max-width: 1400px; padding: 1.5rem 2rem; }

    /* ── Sidebar ── */
    section[data-testid="stSidebar"] {
        background: var(--surface);
        border-right: 1px solid var(--border);
        padding: 0;
    }
    section[data-testid="stSidebar"] > div { padding: 1rem 0.75rem; }
    .sidebar-brand {
        display: flex; align-items: center; gap: 0.6rem;
        padding: 0 0.5rem 0.75rem;
        border-bottom: 1px solid var(--border);
        margin-bottom: 0.5rem;
    }
    .sidebar-brand-icon {
        width: 36px; height: 36px; border-radius: 10px;
        background: linear-gradient(135deg, var(--primary), #7C3AED);
        display: flex; align-items: center; justify-content: center;
        color: white; font-size: 1.1rem; font-weight: 700; flex-shrink: 0;
    }
    .sidebar-brand-text { font-size: 1rem; font-weight: 700; color: var(--text); margin: 0; }
    .sidebar-brand-sub { font-size: 0.7rem; color: var(--text-muted); margin: 0; }
    .nav-section { font-size: 0.65rem; font-weight: 600; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.08em; padding: 0.75rem 0.5rem 0.25rem; }

    section[data-testid="stSidebar"] div[data-testid="stButton"] button {
        justify-content: flex-start; text-align: left;
        padding: 0.55rem 0.75rem; border: none; border-radius: var(--radius-sm);
        box-shadow: none !important; font-size: 0.85rem; font-weight: 500;
        background: transparent; color: var(--text-secondary);
        transition: all 0.15s ease;
    }
    section[data-testid="stSidebar"] div[data-testid="stButton"] button:hover {
        background: #F1F5F9; color: var(--text); border: none;
    }
    section[data-testid="stSidebar"] div[data-testid="stButton"] button[kind="primary"] {
        background: #EFF6FF; color: var(--primary); font-weight: 600;
    }
    section[data-testid="stSidebar"] div[data-testid="stButton"] button[kind="secondary"] {
        background: transparent; color: var(--text-secondary);
    }
    .sidebar-status { padding: 0.75rem 0.5rem; }
    .sidebar-status-label { font-size: 0.65rem; font-weight: 600; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 0.25rem; }

    /* ── Cards ── */
    div[data-testid="stContainer"] { border-radius: var(--radius); }
    div.st-bb { border-color: var(--border) !important; }

    /* ── Metrics ── */
    [data-testid="stMetric"] { background: var(--surface); border-radius: var(--radius); padding: 1rem; border: 1px solid var(--border); box-shadow: var(--shadow); }
    [data-testid="stMetric"] > div { gap: 0; }
    [data-testid="stMetricLabel"] { font-size: 0.75rem; font-weight: 500; color: var(--text-secondary); }
    [data-testid="stMetricValue"] { font-size: 1.5rem !important; font-weight: 700 !important; color: var(--text); }
    [data-testid="stMetricDelta"] { font-size: 0.8rem; }

    /* ── Dataframe ── */
    [data-testid="stDataFrame"] { border-radius: var(--radius-sm); overflow: hidden; border: 1px solid var(--border); }
    .stDataFrame [data-testid="stDataFrameResizable"] { border: none; }
    .stDataFrame thead tr th { background: var(--table_header_bg) !important; color: var(--text-secondary) !important; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.04em; padding: 0.6rem 0.75rem !important; }

    /* ── Buttons ── */
    .stButton button { border-radius: var(--radius-sm); font-weight: 500; font-size: 0.85rem; transition: all 0.15s ease; }
    .stButton button[kind="primary"] { background: var(--primary); border: none; }
    .stButton button[kind="primary"]:hover { background: var(--primary-dark); box-shadow: var(--shadow-md); }

    /* ── Tabs ── */
    .stTabs [data-baseweb="tab-list"] { gap: 0; border-bottom: 1px solid var(--border); }
    .stTabs [data-baseweb="tab"] {
        padding: 0.6rem 1.2rem; font-size: 0.8rem; font-weight: 500;
        color: var(--text-secondary); background: transparent; border: none;
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        color: var(--primary); font-weight: 600;
        border-bottom: 2px solid var(--primary);
    }
    .stTabs [data-baseweb="tab"]:hover { background: #F8FAFC; }

    /* ── Expander ── */
    .streamlit-expanderHeader { font-size: 0.85rem; font-weight: 500; color: var(--text-secondary); border-radius: var(--radius-sm); }
    .streamlit-expander { border: 1px solid var(--border); border-radius: var(--radius); }

    /* ── Progress ── */
    .stProgress .st-bo { background: var(--border); }
    .stProgress .st-bp { background: var(--primary); }

    /* ── Status ── */
    div[data-testid="stStatusWidget"] { border-radius: var(--radius); border: 1px solid var(--border); }

    /* ── Alert / Info ── */
    .stAlert { border-radius: var(--radius-sm); border: none; }

    /* ── Dividers ── */
    hr { border-color: var(--border); margin: 1.5rem 0; }

    /* ── Scrollbar ── */
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: #CBD5E1; border-radius: 3px; }
    ::-webkit-scrollbar-thumb:hover { background: #94A3B8; }

    /* ── Responsive ── */
    @media (max-width: 768px) {
        .main .block-container { padding: 1rem; }
        [data-testid="stMetric"] { padding: 0.75rem; }
        [data-testid="stMetricValue"] { font-size: 1.2rem !important; }
    }
</style>
""", unsafe_allow_html=True)


def _data_freshness_info() -> tuple[str, str]:
    """Return (first_order, last_order) date strings or empty strings."""
    try:
        repo = DuckDBRepository(get_connection())
        if repo.table_exists("orders"):
            df = repo.query(
                "SELECT MIN(order_date) AS first_order, MAX(order_date) AS last_order "
                "FROM orders WHERE order_date IS NOT NULL"
            )
            if df.height > 0:
                first_dt, last_dt = df["first_order"][0], df["last_order"][0]
                fmt = lambda d: d.strftime("%d %b %Y") if hasattr(d, "strftime") else str(d)[:10]
                return (fmt(first_dt) if first_dt else "", fmt(last_dt) if last_dt else "")
    except Exception:
        pass
    return ("", "")


# ── Sidebar ────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="sidebar-brand">
        <div class="sidebar-brand-icon">SB</div>
        <div>
            <p class="sidebar-brand-text">Shopee BI</p>
            <p class="sidebar-brand-sub">Business Intelligence</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    nav_items = [
        ("section", "Main"),
        ("📊", "Dashboard", "Overview & analytics"),
        ("📁", "Upload", "Upload & manage files"),
        ("section", "System"),
        ("⚙️", "Settings", "Configuration"),
    ]

    for item in nav_items:
        if item[0] == "section":
            st.markdown(f'<p class="nav-section">{item[1]}</p>', unsafe_allow_html=True)
        else:
            icon, name, desc = item
            active = st.session_state.page == name
            if st.button(
                f"{icon}  {name}",
                key=f"nav_{name}",
                use_container_width=True,
                type="primary" if active else "secondary",
                help=desc,
            ):
                st.session_state.page = name
                st.rerun()

    st.divider()

    has_data = st.session_state.get("etl_completed")
    st.markdown('<div class="sidebar-status">', unsafe_allow_html=True)
    st.markdown('<p class="sidebar-status-label">Data Status</p>', unsafe_allow_html=True)
    if has_data:
        last = st.session_state.get("last_uploaded", "unknown")
        last_short = str(last)[:30] + "..." if len(str(last)) > 30 else str(last)
        first_date, last_date = _data_freshness_info()
        st.markdown(
            f"<div style='display:flex;align-items:center;gap:0.4rem;margin-bottom:0.25rem;'>"
            f"<span style='color:var(--success);font-size:0.85rem;'>●</span>"
            f"<span style='font-size:0.8rem;font-weight:500;'>Data loaded</span></div>",
            unsafe_allow_html=True,
        )
        st.caption(f"File: {last_short}")
        if last_date:
            st.caption(f"Period: {first_date} — {last_date}")
    else:
        st.markdown(
            f"<div style='display:flex;align-items:center;gap:0.4rem;margin-bottom:0.25rem;'>"
            f"<span style='color:var(--text-muted);font-size:0.85rem;'>○</span>"
            f"<span style='font-size:0.8rem;font-weight:500;'>No data</span></div>",
            unsafe_allow_html=True,
        )
        st.caption("Upload a file to begin")
    st.markdown("</div>", unsafe_allow_html=True)

    st.divider()
    st.caption("v2.0.0 · Premium")

# ── Page routing ───────────────────────────────────────────────────────
page = st.session_state.page

if page == "Dashboard":
    dashboard_page.render()
elif page == "Upload":
    upload.render()
elif page == "Settings":
    settings.render()

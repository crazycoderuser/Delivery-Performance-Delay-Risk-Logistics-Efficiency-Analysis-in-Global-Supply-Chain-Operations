"""
app.py
------
Streamlit entry point for the Supply Chain Delay Risk Dashboard.

Run with:
    streamlit run app/app.py

Features
--------
- Loads and caches cleaned data from data/processed/cleaned_data.csv
- Applies feature engineering (Delay_Gap, Delivery_Classification)
- Exposes four sidebar filters: Shipping Mode, Market, Customer Segment,
  Date Range — all stored in st.session_state so every page can read them
- Displays top-level KPI scorecards on the home page
- Navigation to the four analysis pages is handled automatically by
  Streamlit's multi-page app system (files in app/pages/)
"""

import os
import sys
import streamlit as st
import pandas as pd

# ── Allow src/ imports when launched from any working directory ───────────────
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src.utils import CLEAN_PATH, COL_DELAY_GAP, COL_DELIVERY_CL
from src.feature_engineering import add_delay_features
from src.kpi_metrics import (
    on_time_delivery_rate,
    average_delay,
    late_delivery_risk_ratio,
)

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Supply Chain Delay Risk Dashboard",
    page_icon="🚚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Minimal custom CSS ─────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
        .block-container { padding-top: 1.5rem; }
        [data-testid="metric-container"] {
            background: #f0f4f8;
            border-radius: 8px;
            padding: 12px 16px;
            border-left: 4px solid #0F7B72;
        }
        h1 { color: #1A2E4A; }
        h2 { color: #0F7B72; }
    </style>
    """,
    unsafe_allow_html=True,
)


# ─────────────────────────────────────────────────────────────────────────────
@st.cache_data(show_spinner="Loading dataset…")
def load_data() -> pd.DataFrame:
    """
    Load the cleaned CSV and apply feature engineering.

    Cached with @st.cache_data so the 180k-row read + transformation
    only happens once per session, regardless of how many times widgets
    are changed.

    Returns
    -------
    pd.DataFrame
        Cleaned + feature-engineered dataframe ready for KPI computation.
    """
    if not os.path.exists(CLEAN_PATH):
        st.error(
            f"**Cleaned dataset not found** at `{CLEAN_PATH}`.\n\n"
            "Run the cleaning pipeline first:\n"
            "```\npython src/data_cleaning.py\n```"
        )
        st.stop()

    df = pd.read_csv(CLEAN_PATH)

    # Re-parse dates (CSV read strips datetime dtype)
    for col in ["order date (DateOrders)", "shipping date (DateOrders)"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    df = add_delay_features(df)
    return df


# ─────────────────────────────────────────────────────────────────────────────
def build_sidebar(df: pd.DataFrame) -> pd.DataFrame:
    """
    Render the sidebar filter widgets and return the filtered DataFrame.

    Filters applied:
        1. Shipping Mode   (multiselect)
        2. Market          (multiselect)
        3. Customer Segment (multiselect)
        4. Date Range      (date_input)

    All selected values are stored in st.session_state so child pages
    can read them without re-rendering the sidebar.

    Parameters
    ----------
    df : pd.DataFrame

    Returns
    -------
    pd.DataFrame
        The subset of df matching all active filter conditions.
    """
    st.sidebar.image(
        "https://img.icons8.com/fluency/96/delivery.png",
        width=56,
    )
    st.sidebar.title("🔍 Filters")
    st.sidebar.markdown("---")

    # Shipping Mode
    all_modes = sorted(df["Shipping Mode"].dropna().unique().tolist())
    sel_modes = st.sidebar.multiselect(
        "Shipping Mode",
        options=all_modes,
        default=all_modes,
        key="filter_modes",
    )

    # Market
    all_markets = sorted(df["Market"].dropna().unique().tolist())
    sel_markets = st.sidebar.multiselect(
        "Market",
        options=all_markets,
        default=all_markets,
        key="filter_markets",
    )

    # Customer Segment
    all_segments = sorted(df["Customer Segment"].dropna().unique().tolist())
    sel_segments = st.sidebar.multiselect(
        "Customer Segment",
        options=all_segments,
        default=all_segments,
        key="filter_segments",
    )

    # Date Range
    date_col = "order date (DateOrders)"
    if date_col in df.columns and df[date_col].notna().any():
        min_date = df[date_col].min().date()
        max_date = df[date_col].max().date()
        date_range = st.sidebar.date_input(
            "Order Date Range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date,
            key="filter_dates",
        )
    else:
        date_range = None

    st.sidebar.markdown("---")
    st.sidebar.caption("Filters apply to all dashboard pages.")

    # ── Apply filters ─────────────────────────────────────────────────────────
    mask = (
        df["Shipping Mode"].isin(sel_modes) &
        df["Market"].isin(sel_markets) &
        df["Customer Segment"].isin(sel_segments)
    )

    if date_range and len(date_range) == 2 and date_col in df.columns:
        start, end = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1])
        mask &= df[date_col].between(start, end)

    return df[mask].copy()


# ─────────────────────────────────────────────────────────────────────────────
def render_home(df_filtered: pd.DataFrame) -> None:
    """
    Render the home page: title, KPI scorecards, and a brief intro.

    Parameters
    ----------
    df_filtered : pd.DataFrame
        Filtered dataframe from build_sidebar().
    """
    st.title("🚚 Supply Chain Delay Risk Dashboard")
    st.markdown(
        "Diagnostic intelligence for delivery performance, delay risk, "
        "and logistics efficiency across global supply chain operations."
    )
    st.markdown("---")

    n = len(df_filtered)

    if n == 0:
        st.warning(
            "⚠️ No records match the current filter combination. "
            "Try expanding the filters in the sidebar."
        )
        return

    # ── KPI scorecards ────────────────────────────────────────────────────────
    otr   = on_time_delivery_rate(df_filtered)
    delay = average_delay(df_filtered)
    lrr   = late_delivery_risk_ratio(df_filtered)

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        label="✅ On-Time Delivery Rate",
        value=f"{otr:.1f}%",
        help="% of orders where Delay_Gap = 0 (delivered exactly on schedule)",
    )
    c2.metric(
        label="⏱ Avg Delivery Delay",
        value=f"{delay:+.2f} days",
        delta=f"{delay:+.2f} days vs target",
        delta_color="inverse",
        help="Mean of Delay_Gap = actual − scheduled shipping days",
    )
    c3.metric(
        label="⚠️ Late Delivery Risk Ratio",
        value=f"{lrr:.1%}",
        help="Proportion of orders with Late_delivery_risk = 1",
    )
    c4.metric(
        label="📦 Total Orders",
        value=f"{n:,}",
        help="Number of orders matching current filter selection",
    )

    st.markdown("---")
    st.markdown(
        "### Navigate the dashboard\n"
        "Use the **sidebar pages** to explore deeper analysis:\n\n"
        "- **📊 Delivery Performance** — on-time rate, delay distribution\n"
        "- **⚠️ Delay Risk Analysis** — risk breakdown, high-risk combinations\n"
        "- **🚢 Shipping Mode Comparison** — mode-by-mode efficiency\n"
        "- **🗺️ Regional & Market Heatmaps** — geographic delay concentration"
    )


# ─────────────────────────────────────────────────────────────────────────────
def main() -> None:
    """Main entry point called by Streamlit."""
    df_full     = load_data()
    df_filtered = build_sidebar(df_full)

    # Expose filtered df in session_state so pages can read it
    st.session_state["df_filtered"] = df_filtered
    st.session_state["df_full"]     = df_full

    render_home(df_filtered)


if __name__ == "__main__":
    main()

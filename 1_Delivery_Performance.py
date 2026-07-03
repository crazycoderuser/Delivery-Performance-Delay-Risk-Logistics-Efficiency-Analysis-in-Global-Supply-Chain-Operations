"""
1_Delivery_Performance.py
--------------------------
Page 1: Overall Delivery Performance Overview

Displays:
    - 4-KPI scorecard row
    - Delivery Classification bar chart (On-time / Delayed / Early)
    - Delay Gap distribution histogram
    - Delivery Status breakdown
"""

import os
import sys
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src.utils import COL_DELAY_GAP, COL_DELIVERY_CL, COLOUR_MAP
from src.kpi_metrics import (
    on_time_delivery_rate, average_delay,
    late_delivery_risk_ratio, delay_gap_stats,
    delivery_status_breakdown,
)

st.set_page_config(page_title="Delivery Performance", page_icon="📊", layout="wide")
st.title("📊 Delivery Performance Overview")
st.markdown("Baseline KPIs and delivery timeline analysis across all filtered orders.")
st.markdown("---")


# ── Load filtered data from session state ─────────────────────────────────────
df = st.session_state.get("df_filtered", None)

if df is None or len(df) == 0:
    st.warning(
        "⚠️ No data available. Return to the **Home** page to load the "
        "dataset, or adjust the sidebar filters."
    )
    st.stop()


# ── KPI row ───────────────────────────────────────────────────────────────────
otr   = on_time_delivery_rate(df)
delay = average_delay(df)
lrr   = late_delivery_risk_ratio(df)
stats = delay_gap_stats(df)

c1, c2, c3, c4 = st.columns(4)
c1.metric("✅ On-Time Rate",        f"{otr:.1f}%")
c2.metric("⏱ Avg Delay",           f"{delay:+.2f} days")
c3.metric("⚠️ Late Risk Ratio",    f"{lrr:.1%}")
c4.metric("📦 Orders in View",      f"{len(df):,}")
st.markdown("---")


# ── Row 1: Classification bar + Delay_Gap histogram ──────────────────────────
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Delivery Classification Breakdown")
    counts = df[COL_DELIVERY_CL].value_counts().reset_index()
    counts.columns = ["Classification", "Count"]
    counts["Pct"] = (counts["Count"] / counts["Count"].sum() * 100).round(1)

    fig_bar = px.bar(
        counts,
        x="Classification",
        y="Count",
        color="Classification",
        color_discrete_map=COLOUR_MAP,
        text=counts["Pct"].apply(lambda x: f"{x}%"),
        title="Orders by Delivery Classification",
        labels={"Count": "Number of Orders"},
    )
    fig_bar.update_traces(textposition="outside")
    fig_bar.update_layout(
        showlegend=False,
        plot_bgcolor="white",
        yaxis=dict(gridcolor="#eee"),
        title_font_size=15,
    )
    st.plotly_chart(fig_bar, use_container_width=True)

with col_right:
    st.subheader("Delay Gap Distribution")
    fig_hist = px.histogram(
        df,
        x=COL_DELAY_GAP,
        nbins=30,
        color_discrete_sequence=["#1565C0"],
        title="Distribution of Delivery Delay Gap (days)",
        labels={COL_DELAY_GAP: "Delay Gap (actual − scheduled days)"},
    )
    # Vertical reference line at 0
    fig_hist.add_vline(
        x=0, line_dash="dash", line_color="#C0392B", line_width=2,
        annotation_text="On-time", annotation_position="top right",
    )
    fig_hist.update_layout(
        plot_bgcolor="white",
        yaxis=dict(gridcolor="#eee"),
        title_font_size=15,
    )
    st.plotly_chart(fig_hist, use_container_width=True)


# ── Row 2: Delivery Status breakdown ─────────────────────────────────────────
st.subheader("Delivery Status Breakdown")

if "Delivery Status" in df.columns:
    status_df = delivery_status_breakdown(df)
    col_a, col_b = st.columns([2, 3])

    with col_a:
        st.dataframe(
            status_df.style.format({"pct": "{:.1f}%"}),
            use_container_width=True,
            hide_index=True,
        )

    with col_b:
        fig_status = px.pie(
            status_df,
            names="Delivery Status",
            values="count",
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Set2,
            title="Share by Delivery Status",
        )
        fig_status.update_traces(textinfo="percent+label")
        fig_status.update_layout(title_font_size=15)
        st.plotly_chart(fig_status, use_container_width=True)


# ── Row 3: Delay stats summary ────────────────────────────────────────────────
st.markdown("---")
st.subheader("Delay Gap Statistics")

s1, s2, s3, s4, s5, s6 = st.columns(6)
s1.metric("Mean Delay",    f"{stats.get('mean', 0):+.2f} d")
s2.metric("Median Delay",  f"{stats.get('median', 0):+.2f} d")
s3.metric("Std Dev",       f"{stats.get('std', 0):.2f} d")
s4.metric("% Delayed",     f"{stats.get('pct_delayed', 0):.1f}%")
s5.metric("% On-time",     f"{stats.get('pct_ontime', 0):.1f}%")
s6.metric("% Early",       f"{stats.get('pct_early', 0):.1f}%")

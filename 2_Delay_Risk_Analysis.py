"""
2_Delay_Risk_Analysis.py
------------------------
Page 2: Delay Risk Analysis

Displays:
    - Late_delivery_risk distribution (donut chart)
    - Delay_Gap by Delivery Status (box plot)
    - Top 15 highest-risk Region × Market combinations (table)
    - Delay_Gap over time (line chart if date column available)
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

from src.utils import COL_DELAY_GAP
from src.kpi_metrics import regional_delay_index

st.set_page_config(page_title="Delay Risk Analysis", page_icon="⚠️", layout="wide")
st.title("⚠️ Delay Risk Analysis")
st.markdown("Deep-dive into where and why late delivery risk is concentrated.")
st.markdown("---")


# ── Load data ─────────────────────────────────────────────────────────────────
df = st.session_state.get("df_filtered", None)

if df is None or len(df) == 0:
    st.warning("⚠️ No data — return to Home or adjust sidebar filters.")
    st.stop()


# ── Row 1: Risk distribution donut + box plot ─────────────────────────────────
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Late Delivery Risk Distribution")
    risk_counts = (
        df["Late_delivery_risk"]
        .map({1: "At Risk", 0: "On Schedule"})
        .value_counts()
        .reset_index()
    )
    risk_counts.columns = ["Status", "Count"]

    fig_donut = px.pie(
        risk_counts,
        names="Status",
        values="Count",
        hole=0.5,
        color="Status",
        color_discrete_map={"At Risk": "#C0392B", "On Schedule": "#0F7B72"},
        title="Late_delivery_risk Breakdown",
    )
    fig_donut.update_traces(textinfo="percent+label", pull=[0.04, 0])
    fig_donut.update_layout(title_font_size=15)
    st.plotly_chart(fig_donut, use_container_width=True)

with col_right:
    st.subheader("Delay Gap by Delivery Status")
    if "Delivery Status" in df.columns:
        fig_box = px.box(
            df,
            x="Delivery Status",
            y=COL_DELAY_GAP,
            color="Delivery Status",
            color_discrete_sequence=px.colors.qualitative.Set2,
            title="Delay Gap Distribution per Delivery Status",
            labels={COL_DELAY_GAP: "Delay Gap (days)"},
            points=False,
        )
        fig_box.add_hline(y=0, line_dash="dot", line_color="#555",
                          annotation_text="On-time threshold")
        fig_box.update_layout(
            plot_bgcolor="white",
            yaxis=dict(gridcolor="#eee"),
            showlegend=False,
            title_font_size=15,
        )
        st.plotly_chart(fig_box, use_container_width=True)
    else:
        st.info("'Delivery Status' column not found in dataset.")


# ── Row 2: High-risk region × market table ────────────────────────────────────
st.markdown("---")
st.subheader("Highest-Risk Region × Market Combinations")

if "Order Region" in df.columns and "Market" in df.columns:
    combo = (
        df.groupby(["Market", "Order Region"], observed=True)
        .agg(
            late_rate  = ("Late_delivery_risk", "mean"),
            avg_delay  = (COL_DELAY_GAP,         "mean"),
            volume     = (COL_DELAY_GAP,          "count"),
        )
        .reset_index()
        .sort_values("late_rate", ascending=False)
        .head(15)
    )
    combo["late_rate"]  = (combo["late_rate"]  * 100).round(1).astype(str) + "%"
    combo["avg_delay"]  = combo["avg_delay"].round(2)

    st.dataframe(
        combo.rename(columns={
            "late_rate": "Late Rate (%)",
            "avg_delay": "Avg Delay (days)",
            "volume":    "Order Volume",
        }),
        use_container_width=True,
        hide_index=True,
    )


# ── Row 3: Delay trend over time ──────────────────────────────────────────────
st.markdown("---")
date_col = "order date (DateOrders)"

if date_col in df.columns and df[date_col].notna().any():
    st.subheader("Monthly Avg Delay Gap Over Time")

    monthly = (
        df.set_index(date_col)
        .resample("ME")[COL_DELAY_GAP]
        .mean()
        .reset_index()
    )
    monthly.columns = ["Month", "Avg Delay Gap"]

    fig_line = px.line(
        monthly,
        x="Month",
        y="Avg Delay Gap",
        markers=True,
        title="Monthly Average Delivery Delay Gap",
        labels={"Avg Delay Gap": "Avg Delay Gap (days)"},
        color_discrete_sequence=["#1565C0"],
    )
    fig_line.add_hline(y=0, line_dash="dash", line_color="#C0392B",
                       annotation_text="On-time = 0", annotation_position="top left")
    fig_line.update_layout(
        plot_bgcolor="white",
        yaxis=dict(gridcolor="#eee"),
        title_font_size=15,
    )
    st.plotly_chart(fig_line, use_container_width=True)

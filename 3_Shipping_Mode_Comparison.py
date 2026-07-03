"""
3_Shipping_Mode_Comparison.py
------------------------------
Page 3: Shipping Mode Efficiency Comparison

Displays:
    - Late rate by shipping mode (horizontal bar)
    - Average delay by mode (bar)
    - SLA compliance % by mode (bar)
    - Full mode efficiency summary table
"""

import os
import sys
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src.utils import COL_DELAY_GAP, SHIPPING_COLOURS
from src.kpi_metrics import shipping_mode_efficiency

st.set_page_config(page_title="Shipping Mode Comparison", page_icon="🚢", layout="wide")
st.title("🚢 Shipping Mode Comparison")
st.markdown("Compare on-time rates, average delays, and SLA compliance across each shipping mode.")
st.markdown("---")


# ── Load data ─────────────────────────────────────────────────────────────────
df = st.session_state.get("df_filtered", None)

if df is None or len(df) == 0:
    st.warning("⚠️ No data — return to Home or adjust sidebar filters.")
    st.stop()


mode_df = shipping_mode_efficiency(df)

if mode_df.empty:
    st.info("No shipping mode data available for the current filters.")
    st.stop()


# ── Row 1: Late rate + SLA compliance ────────────────────────────────────────
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Late Delivery Rate by Shipping Mode")
    fig_lr = px.bar(
        mode_df.sort_values("late_rate"),
        x="late_rate",
        y="Shipping Mode",
        orientation="h",
        color="Shipping Mode",
        color_discrete_map=SHIPPING_COLOURS,
        text=mode_df.sort_values("late_rate")["late_rate"].apply(lambda x: f"{x:.1%}"),
        title="Late Rate by Shipping Mode",
        labels={"late_rate": "Late Delivery Rate"},
    )
    fig_lr.update_traces(textposition="outside")
    fig_lr.update_layout(
        showlegend=False,
        plot_bgcolor="white",
        xaxis=dict(gridcolor="#eee", tickformat=".0%"),
        title_font_size=15,
    )
    st.plotly_chart(fig_lr, use_container_width=True)

with col_right:
    st.subheader("SLA Compliance (On-Time Rate) by Mode")
    fig_sla = px.bar(
        mode_df.sort_values("on_time_rate"),
        x="on_time_rate",
        y="Shipping Mode",
        orientation="h",
        color="Shipping Mode",
        color_discrete_map=SHIPPING_COLOURS,
        text=mode_df.sort_values("on_time_rate")["on_time_rate"].apply(lambda x: f"{x:.1%}"),
        title="SLA Compliance % by Shipping Mode",
        labels={"on_time_rate": "On-Time Rate"},
    )
    fig_sla.update_traces(textposition="outside")
    fig_sla.update_layout(
        showlegend=False,
        plot_bgcolor="white",
        xaxis=dict(gridcolor="#eee", tickformat=".0%"),
        title_font_size=15,
    )
    st.plotly_chart(fig_sla, use_container_width=True)


# ── Row 2: Average delay + order volume ──────────────────────────────────────
col_a, col_b = st.columns(2)

with col_a:
    st.subheader("Average Delay Gap by Shipping Mode")
    fig_delay = px.bar(
        mode_df.sort_values("avg_delay"),
        x="avg_delay",
        y="Shipping Mode",
        orientation="h",
        color="avg_delay",
        color_continuous_scale=["#0F7B72", "#FFF3CD", "#C0392B"],
        text=mode_df.sort_values("avg_delay")["avg_delay"].apply(lambda x: f"{x:+.2f}d"),
        title="Average Delivery Delay Gap (days)",
        labels={"avg_delay": "Avg Delay (days)"},
    )
    fig_delay.update_traces(textposition="outside")
    fig_delay.add_vline(x=0, line_dash="dash", line_color="#555")
    fig_delay.update_layout(
        showlegend=False,
        coloraxis_showscale=False,
        plot_bgcolor="white",
        xaxis=dict(gridcolor="#eee"),
        title_font_size=15,
    )
    st.plotly_chart(fig_delay, use_container_width=True)

with col_b:
    st.subheader("Order Volume by Shipping Mode")
    fig_vol = px.pie(
        mode_df,
        names="Shipping Mode",
        values="volume",
        hole=0.4,
        color="Shipping Mode",
        color_discrete_map=SHIPPING_COLOURS,
        title="Share of Orders by Shipping Mode",
    )
    fig_vol.update_traces(textinfo="percent+label")
    fig_vol.update_layout(title_font_size=15)
    st.plotly_chart(fig_vol, use_container_width=True)


# ── Row 3: Full summary table ─────────────────────────────────────────────────
st.markdown("---")
st.subheader("Full Mode Efficiency Summary")

display_df = mode_df.copy()
display_df["late_rate"]    = display_df["late_rate"].apply(lambda x: f"{x:.1%}")
display_df["on_time_rate"] = display_df["on_time_rate"].apply(lambda x: f"{x:.1%}")
display_df["avg_delay"]    = display_df["avg_delay"].apply(lambda x: f"{x:+.2f} days")
display_df = display_df.rename(columns={
    "avg_delay":    "Avg Delay",
    "late_rate":    "Late Rate",
    "on_time_rate": "On-Time Rate",
    "volume":       "Order Volume",
})
st.dataframe(display_df, use_container_width=True, hide_index=True)

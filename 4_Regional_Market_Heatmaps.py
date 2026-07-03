"""
4_Regional_Market_Heatmaps.py
------------------------------
Page 4: Regional & Market Heatmaps

Displays:
    - Plotly scatter_geo map — late rate by Order Country (via lat/lon)
    - Market-level delay index bar chart
    - Order Region delay index bar chart
    - Sortable regional delay table
    - Customer segment impact breakdown
"""

import os
import sys
import streamlit as st
import plotly.express as px
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src.utils import COL_DELAY_GAP
from src.kpi_metrics import regional_delay_index, customer_segment_impact

st.set_page_config(page_title="Regional & Market Heatmaps", page_icon="🗺️", layout="wide")
st.title("🗺️ Regional & Market Heatmaps")
st.markdown("Geographic and market-level concentration of delivery delay risk.")
st.markdown("---")


# ── Load data ─────────────────────────────────────────────────────────────────
df = st.session_state.get("df_filtered", None)

if df is None or len(df) == 0:
    st.warning("⚠️ No data — return to Home or adjust sidebar filters.")
    st.stop()


# ── Geographic scatter map ────────────────────────────────────────────────────
st.subheader("Late Delivery Risk — Global Distribution")

geo_cols = ["Order Country", "Latitude", "Longitude", "Late_delivery_risk"]
if all(c in df.columns for c in geo_cols):
    geo_df = (
        df.groupby(["Order Country", "Latitude", "Longitude"], observed=True)
        .agg(late_rate=("Late_delivery_risk", "mean"), volume=(COL_DELAY_GAP, "count"))
        .reset_index()
    )
    fig_map = px.scatter_geo(
        geo_df,
        lat="Latitude",
        lon="Longitude",
        color="late_rate",
        size="volume",
        hover_name="Order Country",
        hover_data={"late_rate": ":.1%", "volume": ":,", "Latitude": False, "Longitude": False},
        color_continuous_scale=["#0F7B72", "#FFF3CD", "#C0392B"],
        size_max=30,
        title="Late Delivery Risk Rate by Country (bubble size = order volume)",
        labels={"late_rate": "Late Rate"},
    )
    fig_map.update_layout(
        geo=dict(showframe=False, showcoastlines=True, coastlinecolor="#CCC",
                 showland=True, landcolor="#F8F9FA",
                 showocean=True, oceancolor="#EBF5FB"),
        coloraxis_colorbar=dict(title="Late Rate", tickformat=".0%"),
        title_font_size=15,
        height=480,
        margin=dict(l=0, r=0, t=40, b=0),
    )
    st.plotly_chart(fig_map, use_container_width=True)
else:
    st.info("Geographic columns (Order Country, Latitude, Longitude) not found.")

st.markdown("---")


# ── Row: Market + Region bar charts ──────────────────────────────────────────
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Late Rate by Market")
    if "Market" in df.columns:
        mkt_df = regional_delay_index(df, "Market")
        fig_mkt = px.bar(
            mkt_df,
            x="Market",
            y="late_rate",
            color="late_rate",
            color_continuous_scale=["#0F7B72", "#FFF3CD", "#C0392B"],
            text=mkt_df["late_rate"].apply(lambda x: f"{x:.1%}"),
            title="Avg Late Delivery Risk Rate by Market",
            labels={"late_rate": "Late Rate"},
        )
        fig_mkt.update_traces(textposition="outside")
        fig_mkt.update_layout(
            showlegend=False,
            coloraxis_showscale=False,
            plot_bgcolor="white",
            yaxis=dict(gridcolor="#eee", tickformat=".0%"),
            title_font_size=14,
        )
        st.plotly_chart(fig_mkt, use_container_width=True)

with col_right:
    st.subheader("Late Rate by Order Region")
    if "Order Region" in df.columns:
        reg_df = regional_delay_index(df, "Order Region")
        fig_reg = px.bar(
            reg_df.head(12),
            x="late_rate",
            y="Order Region",
            orientation="h",
            color="late_rate",
            color_continuous_scale=["#0F7B72", "#FFF3CD", "#C0392B"],
            text=reg_df.head(12)["late_rate"].apply(lambda x: f"{x:.1%}"),
            title="Top 12 Regions by Late Rate",
            labels={"late_rate": "Late Rate"},
        )
        fig_reg.update_traces(textposition="outside")
        fig_reg.update_layout(
            showlegend=False,
            coloraxis_showscale=False,
            plot_bgcolor="white",
            xaxis=dict(gridcolor="#eee", tickformat=".0%"),
            title_font_size=14,
        )
        st.plotly_chart(fig_reg, use_container_width=True)


# ── Regional delay index table ────────────────────────────────────────────────
st.markdown("---")
st.subheader("Regional Delay Index — Full Table")

group_by = st.selectbox(
    "Group by:",
    options=["Order Region", "Market", "Order Country"],
    index=0,
)

if group_by in df.columns:
    idx_df = regional_delay_index(df, group_by)
    idx_display = idx_df.copy()
    idx_display["late_rate"] = idx_display["late_rate"].apply(lambda x: f"{x:.1%}")
    idx_display["avg_delay"] = idx_display["avg_delay"].apply(lambda x: f"{x:+.2f}d")
    idx_display = idx_display.rename(columns={
        "late_rate": "Late Rate",
        "avg_delay": "Avg Delay",
        "volume":    "Order Volume",
    })
    st.dataframe(idx_display, use_container_width=True, hide_index=True)


# ── Customer segment impact ───────────────────────────────────────────────────
st.markdown("---")
st.subheader("Customer Segment SLA Exposure")

if "Customer Segment" in df.columns and "Sales per customer" in df.columns:
    seg_df = customer_segment_impact(df)

    col_a, col_b = st.columns(2)
    with col_a:
        fig_seg = px.bar(
            seg_df,
            x="Customer Segment",
            y="late_rate",
            color="Customer Segment",
            text=seg_df["late_rate"].apply(lambda x: f"{x:.1%}"),
            title="Late Rate by Customer Segment",
            labels={"late_rate": "Late Rate"},
            color_discrete_sequence=["#1565C0", "#0F7B72", "#E67E22"],
        )
        fig_seg.update_traces(textposition="outside")
        fig_seg.update_layout(
            showlegend=False,
            plot_bgcolor="white",
            yaxis=dict(gridcolor="#eee", tickformat=".0%"),
            title_font_size=14,
        )
        st.plotly_chart(fig_seg, use_container_width=True)

    with col_b:
        seg_display = seg_df.copy()
        seg_display["late_rate"] = seg_display["late_rate"].apply(lambda x: f"{x:.1%}")
        seg_display["avg_delay"] = seg_display["avg_delay"].apply(lambda x: f"{x:+.2f}d")
        seg_display["avg_sales"] = seg_display["avg_sales"].apply(lambda x: f"${x:,.2f}")
        seg_display = seg_display.rename(columns={
            "late_rate": "Late Rate",
            "avg_delay": "Avg Delay",
            "avg_sales": "Avg Sales / Customer",
            "volume":    "Order Volume",
        })
        st.markdown("##### Segment Impact Summary")
        st.dataframe(seg_display, use_container_width=True, hide_index=True)

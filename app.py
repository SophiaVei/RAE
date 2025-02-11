import streamlit as st
import pandas as pd
from data_loader import load_data
from visualizations import (
    plot_permit_distribution,
    plot_installed_capacity,
    create_folium_map,
    plot_permits_over_time,
    plot_technology_growth,
    plot_top_permits,
    plot_energy_mix_per_region,
    plot_expiring_permits,
)
from streamlit_folium import st_folium

# Set full-width layout
st.set_page_config(page_title="Renewable Energy Permits in Greece", layout="wide")

# Load data
df = load_data()

# Dashboard Title
st.title("⚡ Renewable Energy Permits in Greece")

# Tabs for navigation
tab1, tab2, tab3 = st.tabs(["📊 Data Analysis", "🌍 Map", "🔍 Data Table"])

# Exploratory Data Analysis
with tab1:
    st.subheader("📊 Permit Distribution")

    selected_technology_dist = st.multiselect(
        "Select Technology",
        sorted(df["Technology"].unique()),
        key="tech_dist"
    )

    df_filtered_dist = df.copy()
    if selected_technology_dist:
        df_filtered_dist = df_filtered_dist[df_filtered_dist["Technology"].isin(selected_technology_dist)]

    st.plotly_chart(plot_permit_distribution(df_filtered_dist), use_container_width=True)

    st.subheader("📈 Permit Trends Over Time")
    st.plotly_chart(plot_permits_over_time(df), use_container_width=True)

    st.subheader("💡 Growth of Renewable Technologies")
    st.plotly_chart(plot_technology_growth(df), use_container_width=True)

    st.subheader("💡 Installed Capacity by Technology")
    st.plotly_chart(plot_installed_capacity(df), use_container_width=True)

    st.subheader("🔝 Top 10 Largest Permits")
    st.plotly_chart(plot_top_permits(df), use_container_width=True)

    st.subheader("🌞 Energy Mix by Region")
    st.plotly_chart(plot_energy_mix_per_region(df), use_container_width=True)

    st.subheader("⏳ Expiring Permits Timeline")
    st.plotly_chart(plot_expiring_permits(df), use_container_width=True)

# 🌍 Map Visualization
with tab2:
    st.subheader("🌍 Permit Map")

    available_regions = df.dropna(subset=["LAT", "LON"])["Region"].unique()
    available_regions = sorted(available_regions)

    selected_region_map = st.selectbox(
        "Select Region", ["All"] + available_regions, key="region_map_filter"
    )

    selected_technology_map = st.multiselect(
        "Select Technology", sorted(df["Technology"].unique()), key="tech_map"
    )

    @st.cache_data
    def get_filtered_data(region, tech):
        df_filtered = df.dropna(subset=["LAT", "LON"])
        if region != "All":
            df_filtered = df_filtered[df_filtered["Region"] == region]
        if tech:
            df_filtered = df_filtered[df_filtered["Technology"].isin(tech)]
        return df_filtered

    df_filtered_map = get_filtered_data(selected_region_map, selected_technology_map)

    if df_filtered_map.empty:
        st.warning("No data available for the selected filters.")
    else:
        map_object = create_folium_map(df_filtered_map)
        st_folium(map_object, width=900, height=700, key="map")

# Data Table
with tab3:
    st.subheader("🔍 Data Table")
    st.dataframe(df, use_container_width=True)

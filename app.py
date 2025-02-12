import streamlit as st  # ✅ Move st.set_page_config to the top before anything else
st.set_page_config(page_title="Renewable Energy Permits in Greece", layout="wide")  # ✅ Must be first!

import pandas as pd
from data_loader import load_data
from greece_map import create_combined_map
from streamlit_folium import st_folium
from visualizations import (
    plot_permit_distribution,
    plot_installed_capacity,  # ✅ Re-added the missing plot
    plot_permits_over_time,
    plot_technology_growth,
    plot_top_permits,
    plot_energy_mix_per_region,
    plot_expiring_permits,
)

# Load data
df = load_data()

# Dashboard Title
st.title("⚡ Renewable Energy Permits in Greece")

# Tabs for navigation
tab1, tab2, tab3 = st.tabs(["📊 Data Analysis", "🌍 Map", "🔍 Data Table"])

# ✅ **Tab 1: Data Analysis**
with tab1:
    st.subheader("📊 Permit Distribution")
    st.plotly_chart(plot_permit_distribution(df), use_container_width=True)

    st.subheader("📈 Permit Trends Over Time")
    st.plotly_chart(plot_permits_over_time(df), use_container_width=True)

    st.subheader("💡 Growth of Renewable Technologies")
    st.plotly_chart(plot_technology_growth(df), use_container_width=True)

    st.subheader("💡 Installed Capacity by Technology")  # ✅ Re-added!
    st.plotly_chart(plot_installed_capacity(df), use_container_width=True)

    st.subheader("🔝 Top 10 Largest Permits")
    st.plotly_chart(plot_top_permits(df), use_container_width=True)

    st.subheader("🌞 Energy Mix by Region")
    st.plotly_chart(plot_energy_mix_per_region(df), use_container_width=True)

    st.subheader("⏳ Expiring Permits Timeline")
    st.plotly_chart(plot_expiring_permits(df), use_container_width=True)

# ✅ **Tab 2: Interactive Map**
with tab2:
    st.subheader("🌍 Map of Greece's Renewable Energy Permits")

    # Generate the map
    map_object = create_combined_map()

    # Display the map in full-screen
    st_folium(map_object, use_container_width=True, height=900, key="combined_map")
    st.markdown("""
        <style>
            .main .block-container {
                padding: 0rem !important;
            }
            .leaflet-control-attribution, 
            .leaflet-bottom, 
            .leaflet-control-layers, 
            .leaflet-container a, 
            .leaflet-bar {
                display: none !important;
                visibility: hidden !important;
                opacity: 0 !important;
                width: 0 !important;
                height: 0 !important;
            }
        </style>
    """, unsafe_allow_html=True)

# ✅ **Tab 3: Data Table**
with tab3:
    st.subheader("🔍 Data Table")

    # ✅ Drop the "Year" column if it exists
    df_display = df.drop(columns=["Year"], errors="ignore")

    # ✅ Display the DataFrame without the "Year" column
    st.dataframe(df_display, use_container_width=True)


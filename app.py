import streamlit as st
import pandas as pd
import numpy as np
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
from streamlit_folium import st_folium  # Use st_folium instead of folium_static

# Load data
df = load_data()

# Dashboard Title
st.title("⚡️ Ενεργειακές Άδειες ΑΠΕ στην Ελλάδα")

# Tabs for navigation
tab1, tab2, tab3 = st.tabs(["📊 Ανάλυση Δεδομένων", "🌍 Χάρτης", "🔍 Παρατηρητήριο"])

# Exploratory Data Analysis
with tab1:
    st.subheader("📊 Κατανομή Αδειών")

    selected_technology_dist = st.multiselect(
        "Επιλέξτε Τεχνολογία",
        sorted(df["ΤΕΧΝΟΛΟΓΙΑ"].unique()),
        key="tech_dist"
    )

    df_filtered_dist = df.copy()
    if selected_technology_dist:
        df_filtered_dist = df_filtered_dist[df_filtered_dist["ΤΕΧΝΟΛΟΓΙΑ"].isin(selected_technology_dist)]

    st.plotly_chart(plot_permit_distribution(df_filtered_dist))

    st.subheader("📈 Εξέλιξη Αδειών με την Πάροδο του Χρόνου")
    st.plotly_chart(plot_permits_over_time(df))

    st.subheader("💡 Ανάπτυξη Τεχνολογιών ΑΠΕ")
    st.plotly_chart(plot_technology_growth(df))

    st.subheader("💡 Ισχύς ανά Τεχνολογία")

    selected_region_cap = st.selectbox(
        "Επιλέξτε Περιφέρεια", ["Όλες"] + sorted(df["ΠΕΡΙΦΕΡΕΙΑ"].unique()), key="region_cap"
    )
    selected_technology_cap = st.multiselect(
        "Επιλέξτε Τεχνολογία",
        sorted(df["ΤΕΧΝΟΛΟΓΙΑ"].unique()),
        key="tech_cap"
    )

    df_filtered_cap = df.copy()
    if selected_region_cap != "Όλες":
        df_filtered_cap = df_filtered_cap[df_filtered_cap["ΠΕΡΙΦΕΡΕΙΑ"] == selected_region_cap]

    if selected_technology_cap:
        df_filtered_cap = df_filtered_cap[df_filtered_cap["ΤΕΧΝΟΛΟΓΙΑ"].isin(selected_technology_cap)]

    st.plotly_chart(plot_installed_capacity(df_filtered_cap))

    st.subheader("🔝 Οι 10 Μεγαλύτερες Άδειες ΑΠΕ")
    st.plotly_chart(plot_top_permits(df))

# Map Visualization
with tab2:
    st.subheader("🌍 Χάρτης Αδειών ΑΠΕ")

    selected_region_map = st.selectbox(
        "Επιλέξτε Περιφέρεια", ["Όλες"] + sorted(df["ΠΕΡΙΦΕΡΕΙΑ"].unique()), key="region_map"
    )
    selected_technology_map = st.multiselect(
        "Επιλέξτε Τεχνολογία",
        sorted(df["ΤΕΧΝΟΛΟΓΙΑ"].unique()),
        key="tech_map"
    )

    df_filtered_map = df.copy()
    if selected_region_map != "Όλες":
        df_filtered_map = df_filtered_map[df_filtered_map["ΠΕΡΙΦΕΡΕΙΑ"] == selected_region_map]

    if selected_technology_map:
        df_filtered_map = df_filtered_map[df_filtered_map["ΤΕΧΝΟΛΟΓΙΑ"].isin(selected_technology_map)]

    map_object = create_folium_map(df_filtered_map)
    st_folium(map_object, width=700, height=700)

    st.subheader("🌞 Ενεργειακό Μείγμα Ανά Περιφέρεια")
    st.plotly_chart(plot_energy_mix_per_region(df))

# Data Observations
with tab3:
    st.subheader("⏳ Χρονοδιάγραμμα Λήξεων Αδειών")
    st.plotly_chart(plot_expiring_permits(df))

    st.subheader("🔍 Πίνακας Δεδομένων")

    selected_region_table = st.selectbox(
        "Επιλέξτε Περιφέρεια", ["Όλες"] + sorted(df["ΠΕΡΙΦΕΡΕΙΑ"].unique()), key="region_table"
    )
    selected_technology_table = st.multiselect(
        "Επιλέξτε Τεχνολογία",
        sorted(df["ΤΕΧΝΟΛΟΓΙΑ"].unique()),
        key="tech_table"
    )

    df_filtered_table = df.copy()
    if selected_region_table != "Όλες":
        df_filtered_table = df_filtered_table[df_filtered_table["ΠΕΡΙΦΕΡΕΙΑ"] == selected_region_table]

    if selected_technology_table:
        df_filtered_table = df_filtered_table[df_filtered_table["ΤΕΧΝΟΛΟΓΙΑ"].isin(selected_technology_table)]

    st.dataframe(df_filtered_table)

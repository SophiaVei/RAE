import streamlit as st
import folium
import json
import pandas as pd
from streamlit_folium import st_folium
import os
from folium.plugins import MarkerCluster

# ✅ Load Greece administrative regions GeoJSON
geojson_path = "data/geo/greece-regions.geojson"

@st.cache_data
def load_geojson():
    """Load the GeoJSON file containing Greece's administrative regions."""
    with open(geojson_path, "r", encoding="utf-8") as f:
        return json.load(f)

@st.cache_data
def load_permit_data():
    """Load the processed permit data."""
    file_path = "data/permits/final_permits_cleaned.xlsx"
    df = pd.read_excel(file_path)
    return df.dropna(subset=["LAT", "LON"])  # ✅ Drop rows without coordinates for speed

def region_style(feature):
    """Define a modern blue style for the regions."""
    return {
        "fillColor": "#b8edea",  # Light blue
        "color": "#8ccdc0",  # Soft blue border
        "weight": 2,
        "fillOpacity": 0.7,
    }

def highlight_region(feature):
    """Highlight function for hover effect."""
    return {"weight": 3, "fillOpacity": 0.9, "color": "#93C5FD"}  # Light blue glow

@st.cache_data
def create_combined_map():
    """Create a sleek, modern full-screen Folium map with Greece's regions and permits."""
    greece_geojson = load_geojson()
    permit_df = load_permit_data()

    # ✅ Aggregate permit stats by region
    permit_summary = permit_df.groupby("Region").agg({
        "Permit ID": "count",
        "Installed Capacity (MW)": "sum"
    }).reset_index()

    permit_summary_dict = permit_summary.set_index("Region").to_dict(orient="index")

    # ✅ FIX: Create a Folium map and manually remove attribution
    greece_map = folium.Map(
        location=[38.0, 23.7],
        zoom_start=7,
        tiles="CartoDB Positron",
        attr=" "  # ✅ Set empty attribution (not always enough)
    )

    # ✅ Remove any residual attribution elements dynamically
    for name, layer in list(greece_map._children.items()):
        if "attribution" in name.lower():
            del greece_map._children[name]

    # ✅ Add regions layer from GeoJSON
    folium.GeoJson(
        greece_geojson,
        name="Regions",
        tooltip=folium.GeoJsonTooltip(
            fields=["name"], aliases=["Region:"], style="font-size: 14px; font-weight: bold; color: #2563EB;"
        ),
        popup=folium.GeoJsonPopup(fields=["name"], aliases=["Region:"], style="font-size: 14px; color: #1E3A8A;"),
        style_function=region_style,
        highlight_function=highlight_region,
    ).add_to(greece_map)

    # ✅ Generate cluster data using MarkerCluster
    marker_cluster = MarkerCluster().add_to(greece_map)

    for region, stats in permit_summary_dict.items():
        total_permits = stats["Permit ID"]
        total_capacity = stats["Installed Capacity (MW)"]

        # Get the first valid latitude & longitude for this region
        region_data = permit_df[permit_df["Region"] == region].iloc[0]
        lat, lon = region_data["LAT"], region_data["LON"]

        # ✅ Add marker with permit count & hover info (New color: `#8ccdc0`)
        folium.Marker(
            location=[lat, lon],
            icon=folium.DivIcon(html=f"""
                <div style="background-color:#8ccdc0;
                            border-radius:50%;
                            width:40px;height:40px;
                            line-height:40px;
                            text-align:center;
                            color:white;
                            font-weight:bold;">
                    {total_permits}
                </div>
            """),
            popup=f"""
                <b style="color:#2563EB;">Region:</b> {region}<br>
                🔹 <b>Total Permits:</b> {total_permits}<br>
                ⚡ <b>Total Installed Capacity:</b> {total_capacity:.2f} MW
            """
        ).add_to(marker_cluster)

    return greece_map

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

geojson_path_units = "data/geo/greece-prefectures.geojson"

@st.cache_data
def load_geojson_units():
    """Load the GeoJSON file containing Greece's regional units (prefectures)."""
    with open(geojson_path_units, "r", encoding="utf-8") as f:
        return json.load(f)

@st.cache_data
def load_permit_data():
    """Load the processed permit data."""
    file_path = "data/permits/final_permits_cleaned.xlsx"
    df = pd.read_excel(file_path)
    return df.dropna(subset=["LAT", "LON"])  # ✅ Drop rows without coordinates for speed

def get_technology_breakdown(df, region_column, region_value):
    """Get installed capacity breakdown by technology for a given region or regional unit."""
    breakdown = df[df[region_column] == region_value].groupby("Technology")["Installed Capacity (MW)"].sum()
    if breakdown.empty:
        return "No data available"
    return "<br>".join([f"{tech}: {capacity:.2f} MW" for tech, capacity in breakdown.items()])

### 🌍 **REGION MAP**
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

    # ✅ Create the Folium map
    greece_map = folium.Map(
        location=[38.0, 23.7],
        zoom_start=7,
        tiles="CartoDB Positron",
        attr=" "
    )

    # ✅ Remove any residual attribution elements dynamically
    for name, layer in list(greece_map._children.items()):
        if "attribution" in name.lower():
            del greece_map._children[name]

    # ✅ Add regions layer from GeoJSON
    folium.GeoJson(
        greece_geojson,
        name="Regions",
        tooltip=folium.GeoJsonTooltip(fields=["name"], aliases=["Region:"]),
        popup=folium.GeoJsonPopup(fields=["name"], aliases=["Region:"]),
        style_function=region_style,
        highlight_function=highlight_region,
    ).add_to(greece_map)

    # ✅ Generate cluster data using MarkerCluster
    marker_cluster = MarkerCluster().add_to(greece_map)

    for region, stats in permit_summary_dict.items():
        total_permits = stats["Permit ID"]
        total_capacity = stats["Installed Capacity (MW)"]

        # Get technology breakdown for this region
        tech_breakdown = get_technology_breakdown(permit_df, "Region", region)

        # Get the first valid latitude & longitude for this region
        region_data = permit_df[permit_df["Region"] == region].iloc[0]
        lat, lon = region_data["LAT"], region_data["LON"]

        # ✅ Add marker with permit count & detailed hover info
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
                <b>Region:</b> {region}<br>
                🔹 <b>Total Permits:</b> {total_permits}<br>
                ⚡ <b>Total Installed Capacity:</b> {total_capacity:.2f} MW<br>
                <b>Technology Breakdown:</b><br>{tech_breakdown}
            """
        ).add_to(marker_cluster)

    return greece_map


### 🏛 **REGIONAL UNITS MAP**
def create_prefecture_map():
    """Create a sleek, modern Folium map for Greece's **regional units (prefectures)**."""
    greece_geojson_units = load_geojson_units()
    permit_df = load_permit_data()

    # ✅ Filter out rows where LAT_UNIT or LON_UNIT are NaN
    permit_df_units = permit_df.dropna(subset=["LAT_UNIT", "LON_UNIT"])

    # Aggregate permit stats by Regional Unit
    permit_summary_units = permit_df_units.groupby("Regional Unit English").agg({
        "Permit ID": "count",
        "Installed Capacity (MW)": "sum"
    }).reset_index()

    permit_summary_units_dict = permit_summary_units.set_index("Regional Unit English").to_dict(orient="index")

    # ✅ Create the Folium map for Prefectures
    prefecture_map = folium.Map(
        location=[38.0, 23.7],
        zoom_start=7,
        tiles="CartoDB Positron",
        attr=" "
    )

    # ✅ Add Regional Units Layer
    folium.GeoJson(
        greece_geojson_units,
        name="Regional Units",
        tooltip=folium.GeoJsonTooltip(fields=["name"], aliases=["Prefecture:"]),
        popup=folium.GeoJsonPopup(fields=["name"], aliases=["Prefecture:"]),
        style_function=region_style,
        highlight_function=highlight_region,
    ).add_to(prefecture_map)

    # ✅ Generate cluster data using MarkerCluster
    marker_cluster = MarkerCluster().add_to(prefecture_map)

    # ✅ Add markers for **Regional Units** (Only the ones with coordinates)
    for unit, stats in permit_summary_units_dict.items():
        total_permits = stats["Permit ID"]
        total_capacity = stats["Installed Capacity (MW)"]

        # Get technology breakdown for this regional unit
        tech_breakdown = get_technology_breakdown(permit_df_units, "Regional Unit English", unit)

        unit_data = permit_df_units[permit_df_units["Regional Unit English"] == unit].iloc[0]
        lat, lon = unit_data["LAT_UNIT"], unit_data["LON_UNIT"]

        # ✅ Add marker with permit count & hover info
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
                <b>Regional Unit:</b> {unit}<br>
                🔹 <b>Total Permits:</b> {total_permits}<br>
                ⚡ <b>Total Installed Capacity:</b> {total_capacity:.2f} MW<br>
                <b>Technology Breakdown:</b><br>{tech_breakdown}
            """
        ).add_to(marker_cluster)

    return prefecture_map


### **🌈 STYLING FUNCTIONS**
def region_style(feature):
    """Define a modern blue style for the regions & prefectures."""
    return {
        "fillColor": "#b8edea",  # Light blue (same for both maps)
        "color": "#8ccdc0",  # Soft blue border
        "weight": 2,
        "fillOpacity": 0.7,
    }

def highlight_region(feature):
    """Highlight function for hover effect (same for both)."""
    return {"weight": 3, "fillOpacity": 0.9, "color": "#93C5FD"}

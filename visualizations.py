import streamlit as st
import plotly.express as px
import folium
from streamlit_folium import folium_static
from folium.plugins import FastMarkerCluster

def plot_permit_distribution(df):
    """Bar chart of permits per region."""
    permit_counts = df["Region"].value_counts().reset_index()
    permit_counts.columns = ["Region", "Number of Permits"]

    fig = px.bar(permit_counts, x="Region", y="Number of Permits",
                 title="Distribution of Renewable Energy Permits by Region")

    fig.update_layout(width=600, height=800)  # Square aspect ratio
    return fig

def plot_installed_capacity(df):
    """Pie chart of installed MW per technology."""
    capacity = df.groupby("Technology")["Installed Capacity (MW)"].sum().reset_index()

    fig = px.pie(capacity, values="Installed Capacity (MW)", names="Technology",
                 title="Installed Capacity (MW) by Technology")

    fig.update_layout(width=600, height=600)  # Square aspect ratio
    return fig

@st.cache_data
def create_folium_map(df_filtered):
    """Precompute the Folium map ONCE and store it to avoid unnecessary recalculations."""
    greece_map = folium.Map(location=[38.0, 23.7], zoom_start=6, tiles="CartoDB positron")

    if df_filtered.empty:
        return greece_map  # Return an empty map if no data

    # Use FastMarkerCluster for better performance
    FastMarkerCluster(
        data=df_filtered[["LAT", "LON"]].values.tolist()
    ).add_to(greece_map)

    return greece_map

def plot_permits_over_time(df):
    """Line chart of permits issued over time."""
    df["Year"] = df["Application Submission Date"].dt.year
    permits_per_year = df.groupby("Year").size().reset_index(name="Number of Permits")

    fig = px.line(
        permits_per_year, x="Year", y="Number of Permits",
        title="📈 Trend of Renewable Energy Permits Over Time",
        markers=True
    )

    fig.update_layout(width=600, height=600)  # Square aspect ratio
    return fig

def plot_technology_growth(df):
    """Stacked area chart showing technology trends over time."""
    df["Year"] = df["Application Submission Date"].dt.year
    tech_trends = df.groupby(["Year", "Technology"])["Installed Capacity (MW)"].sum().reset_index()

    fig = px.area(
        tech_trends, x="Year", y="Installed Capacity (MW)", color="Technology",
        title="📊 Growth of Renewable Energy Technologies Over Time",
        line_group="Technology"
    )

    fig.update_layout(width=600, height=600)  # Square aspect ratio
    return fig

def plot_top_permits(df):
    """Bar chart of the top 10 largest permits."""
    top_permits = df.nlargest(10, "Installed Capacity (MW)")

    fig = px.bar(
        top_permits, x="Installed Capacity (MW)", y="Permit ID",
        title="🔝 Top 10 Largest Renewable Energy Permits",
        orientation='h'
    )

    fig.update_layout(width=600, height=600)  # Square aspect ratio
    return fig

def plot_energy_mix_per_region(df):
    """Sunburst chart of energy mix per region."""
    fig = px.sunburst(
        df, path=["Region", "Technology"], values="Installed Capacity (MW)",
        title="🌞 Energy Mix by Region and Technology"
    )

    fig.update_layout(width=600, height=600)  # Square aspect ratio
    return fig

def plot_expiring_permits(df):
    """Histogram of expiring permits per year."""
    df["Year"] = df["Permit Expiration Date"].dt.year
    expiration_counts = df["Year"].value_counts().reset_index()
    expiration_counts.columns = ["Year", "Number of Permits"]

    fig = px.bar(
        expiration_counts, x="Year", y="Number of Permits",
        title="⏳ Expiring Renewable Energy Permits",
    )

    fig.update_layout(width=600, height=600)  # Square aspect ratio
    return fig

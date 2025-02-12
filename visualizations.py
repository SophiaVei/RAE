import streamlit as st
import plotly.express as px
import folium
from streamlit_folium import folium_static
from folium.plugins import FastMarkerCluster

import plotly.express as px


import plotly.express as px

def plot_permit_distribution(df):
    """Bar chart of permits per region with limited company names on hover, preserving order."""

    # Ensure "Company" is a string and handle NaN values
    df["Company"] = df["Company"].fillna("Unknown").astype(str)

    # Count the number of permits per region (preserving the order)
    permit_counts = df["Region"].value_counts().reset_index()
    permit_counts.columns = ["Region", "Number of Permits"]

    # Extract unique company names for each region (preserving the order)
    company_info = df.groupby("Region")["Company"].unique().to_dict()

    # Limit hover text to the first 10 companies, then add "... and X more"
    def format_company_list(companies):
        max_companies = 10  # ✅ Show only 10 companies
        if len(companies) > max_companies:
            return "<br>".join(companies[:max_companies]) + f"<br>... and {len(companies) - max_companies} more"
        return "<br>".join(companies)

    permit_counts["Company"] = permit_counts["Region"].map(company_info)
    permit_counts["Company"] = permit_counts["Company"].apply(format_company_list)

    fig = px.bar(
        permit_counts,
        x="Region",
        y="Number of Permits",
        hover_data={"Company": True},  # ✅ Show company names on hover
        title="📊 Distribution of Renewable Energy Permits by Region",
        color_discrete_sequence=["#8ccdc0"]  # ✅ Modern bar color
    )

    fig.update_traces(
        hovertemplate="<b>%{x}</b><br>🔹 Companies:<br>%{customdata[0]}"  # ✅ Show limited companies only on hover
    )

    fig.update_layout(
        xaxis=dict(title="", tickangle=45, tickfont=dict(size=14)),  # ✅ Slanted labels for readability
        yaxis=dict(title="Number of Permits", gridcolor="lightgray"),  # ✅ Grid for better readability
        title=dict(font=dict(size=18)),  # ✅ Centered title
        plot_bgcolor="white",  # ✅ Clean background
        width=600, height=800  # ✅ Square aspect ratio
    )

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
    """Line chart of permits issued over time with a consistent modern color theme."""

    df["Year"] = df["Application Submission Date"].dt.year
    permits_per_year = df.groupby("Year").size().reset_index(name="Number of Permits")

    fig = px.line(
        permits_per_year,
        x="Year",
        y="Number of Permits",
        title="📈 Trend of Renewable Energy Permits Over Time",
        markers=True
    )

    # ✅ Apply consistent color styling (Line + Markers)
    fig.update_traces(
        line=dict(color="#93C5FD", width=2),  # ✅ Set line color & width
        marker=dict(color="#8ccdc0", size=6)  # ✅ Set marker color & size
    )

    fig.update_layout(
        width=600, height=600,  # ✅ Square aspect ratio
        xaxis=dict(title="Year", tickangle=-45, tickfont=dict(size=14)),  # ✅ Slanted labels for readability
        yaxis=dict(title="Number of Permits", gridcolor="lightgray"),  # ✅ Grid for better visibility
        title=dict(font=dict(size=18), x=0.5),  # ✅ Centered title
        plot_bgcolor="white",  # ✅ Clean background
        showlegend=False,  # ✅ Hide legend (since it's a single line)
    )

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
    """Histogram of expiring permits per year with a modern and consistent design."""

    df["Year"] = df["Permit Expiration Date"].dt.year
    expiration_counts = df["Year"].value_counts().reset_index()
    expiration_counts.columns = ["Year", "Number of Permits"]
    expiration_counts = expiration_counts.sort_values(by="Year")  # ✅ Ensure chronological order

    fig = px.bar(
        expiration_counts,
        x="Year",
        y="Number of Permits",
        title="⏳ Expiring Renewable Energy Permits",
        color_discrete_sequence=["#93C5FD"]  # ✅ Modern color consistency
    )

    # ✅ Improve styling for a cleaner and more professional look
    fig.update_traces(
        textposition="outside"  # ✅ Display numbers above bars
    )

    fig.update_layout(
        xaxis=dict(title="Year", tickangle=-45, tickfont=dict(size=14)),  # ✅ Slanted labels for better readability
        yaxis=dict(title="Number of Permits", gridcolor="lightgray"),  # ✅ Subtle gridlines for better visibility
        title=dict(font=dict(size=18), x=0.5),  # ✅ Center title
        plot_bgcolor="white",  # ✅ Clean background
        width=600, height=800  # ✅ Square aspect ratio
    )

    return fig

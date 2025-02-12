import streamlit as st
import plotly.express as px
import folium
from streamlit_folium import folium_static
from folium.plugins import FastMarkerCluster
import random

technology_colors = {
    "ΑΙΟΛΙΚΑ": "#d9ead3",  # Deep Blue
    "ΒΙΟΜΑΖΑ": "#3B82F6",  # Lighter Blue
    "ΜΥΗΕ": "#60A5FA",  # Sky Blue
    "ΦΩΤΟΒΟΛΤΑΙΚΑ": "#ff2e79",  # Green
    "ΒΙΟΜΑΖΑ-ΒΙΟΑΕΡΙΟ": "#A3E635",  # Light Green
    "ΒΙΟΜΑΖΑ-ΚΑΥΣΗ": "#FACC15",  # Yellow
    "ΗΛΙΟΘΕΡΜΙΚΑ": "#F97316",  # Orange
}


def plot_permit_distribution(df):
    """Stacked bar chart of permits per region, segmented by Technology, preserving original order with company names on hover."""

    # Ensure correct data types
    df["Technology"] = df["Technology"].astype(str)
    df["Company"] = df["Company"].fillna("Unknown").astype(str)  # Ensure no NaNs in company names

    # **Step 1: Preserve Original Order of Regions**
    region_order = df["Region"].value_counts().index.tolist()  # Get region order based on count

    # **Step 2: Aggregate Number of Permits per Region per Technology**
    permit_counts = df.groupby(["Region", "Technology"]).size().reset_index(name="Number of Permits")

    # **Step 3: Extract Unique Company Names for Each Region**
    company_info = df.groupby("Region")["Company"].unique().to_dict()

    # **Step 4: Format Company List for Hover**
    def format_company_list(companies):
        max_companies = 10  # ✅ Show only 10 companies
        if len(companies) > max_companies:
            return "<br>".join(companies[:max_companies]) + f"<br>... and {len(companies) - max_companies} more"
        return "<br>".join(companies)

    permit_counts["Company"] = permit_counts["Region"].map(company_info)
    permit_counts["Company"] = permit_counts["Company"].apply(format_company_list)

    # ✅ **Step 5: Stacked Bar Chart (Preserving Region Order)**
    fig = px.bar(
        permit_counts,
        x="Region",
        y="Number of Permits",
        color="Technology",  # ✅ Stack by Technology
        title="📊 Distribution of Renewable Energy Permits by Region (Segmented by Technology)",
        barmode="stack",  # ✅ Stacked bars
        color_discrete_map=technology_colors,  # ✅ Use fixed colors
        hover_data={"Company": True}  # ✅ Show company names on hover
    )

    # ✅ **Step 6: Apply Fixed Region Order**
    fig.update_xaxes(categoryorder="array", categoryarray=region_order)  # ✅ Preserve original region order

    # ✅ **Step 7: Improve Styling**
    fig.update_traces(
        hovertemplate="<b>%{x}</b><br>🔹 Companies:<br>%{customdata[0]}"  # ✅ Show limited companies only on hover
    )

    fig.update_layout(
        xaxis=dict(title="", tickangle=-45, tickfont=dict(size=14)),  # ✅ Slanted labels for readability
        yaxis=dict(title="Number of Permits", gridcolor="lightgray"),  # ✅ Subtle gridlines for better visibility
        plot_bgcolor="white",  # ✅ Clean background
        width=600, height=800,  # ✅ Square aspect ratio
        legend=dict(title="Technology", font=dict(size=12))  # ✅ Add a legend box
    )

    return fig




def plot_installed_capacity(df):
    """Pie chart of installed MW per technology."""
    capacity = df.groupby("Technology")["Installed Capacity (MW)"].sum().reset_index()

    fig = px.pie(
        capacity,
        values="Installed Capacity (MW)",
        names="Technology",
        color="Technology",
        color_discrete_map=technology_colors  # ✅ Apply fixed colors
    )

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

    df["Year"] = df["Application Submission Date"].dt.year
    permits_per_year = df.groupby("Year").size().reset_index(name="Number of Permits")

    fig = px.line(
        permits_per_year,
        x="Year",
        y="Number of Permits",
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
        line_group="Technology",
        color_discrete_map=technology_colors  # ✅ Apply fixed colors
    )

    fig.update_layout(width=600, height=600)  # Square aspect ratio
    return fig



def plot_top_permits(df):
    """Bar chart of the top 10 largest permits, colored by Technology with a legend."""

    # Get the top 10 permits by installed capacity
    top_permits = df.nlargest(10, "Installed Capacity (MW)").copy()

    # Ensure Technology is treated as a category
    top_permits["Technology"] = top_permits["Technology"].astype(str)

    fig = px.bar(
        top_permits,
        x="Installed Capacity (MW)",
        y="Permit ID",
        color="Technology",  # ✅ Color bars by Technology
        color_discrete_map=technology_colors,  # ✅ Use fixed colors
        orientation='h'
    )

    fig.update_layout(
        width=600, height=600,  # ✅ Square aspect ratio
        xaxis=dict(title="Installed Capacity (MW)", tickfont=dict(size=14)),
        yaxis=dict(title="Permit ID", tickfont=dict(size=14)),
        plot_bgcolor="white",  # ✅ Clean background
        legend=dict(title="Technology", font=dict(size=12)),  # ✅ Add a legend box
    )

    return fig



def plot_energy_mix_per_region(df):
    """Sunburst chart of energy mix per region."""
    fig = px.sunburst(
        df, path=["Region", "Technology"], values="Installed Capacity (MW)",
    )

    fig.update_layout(width=600, height=600)  # Square aspect ratio
    return fig



def plot_expiring_permits(df):
    """Stacked bar chart of expiring permits per year, split by Technology."""

    # Ensure correct data types
    df["Year"] = df["Permit Expiration Date"].dt.year.astype(int)  # Convert to int for sorting
    df["Technology"] = df["Technology"].astype(str)  # Ensure Technology is string

    # Aggregate the number of permits per year per Technology
    expiration_counts = df.groupby(["Year", "Technology"]).size().reset_index(name="Number of Permits")

    # ✅ Use a stacked bar chart to show expiration by Technology
    fig = px.bar(
        expiration_counts,
        x="Year",
        y="Number of Permits",
        color="Technology",  # ✅ Stack by Technology
        barmode="stack",  # ✅ Stacked bars
        color_discrete_map=technology_colors  # ✅ Use fixed colors
    )

    # ✅ Improve styling for a cleaner and more professional look
    fig.update_traces(
        textposition="inside"  # ✅ Display numbers inside bars
    )

    fig.update_layout(
        xaxis=dict(title="Year", tickangle=-45, tickfont=dict(size=14)),  # ✅ Slanted labels for better readability
        yaxis=dict(title="Number of Permits", gridcolor="lightgray"),  # ✅ Subtle gridlines for better visibility
        plot_bgcolor="white",  # ✅ Clean background
        width=600, height=800,  # ✅ Square aspect ratio
        legend=dict(title="Technology", font=dict(size=12))  # ✅ Add a legend box
    )

    return fig

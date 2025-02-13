import streamlit as st
import plotly.graph_objects as go
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


def plot_permits_over_time(df, fire_df, selected_fire_metric):
    """Line chart of permits issued over time with dynamic selection for fire data."""

    df["Year"] = df["Application Submission Date"].dt.year
    permits_per_year = df.groupby("Year").size().reset_index(name="Number of Permits")

    fig = go.Figure()

    # ✅ Primary Y-Axis: Number of Permits (Blue)
    fig.add_trace(
        go.Scatter(
            x=permits_per_year["Year"],
            y=permits_per_year["Number of Permits"],
            mode="lines+markers",
            name="Number of Permits",
            line=dict(color="#93C5FD", width=2),
            marker=dict(color="#8ccdc0", size=6),
            yaxis="y1",
        )
    )

    # ✅ Secondary Y-Axis: Number of Fires (Red)
    if selected_fire_metric == "Number of Fires":
        fig.add_trace(
            go.Scatter(
                x=fire_df["Year"],
                y=fire_df["Number of Fires"],
                mode="lines+markers",
                name="Number of Fires",
                line=dict(color="red", dash="dash"),
                marker=dict(color="red", size=6),
                yaxis="y2",
            )
        )

    # ✅ Tertiary Y-Axis: Burned Area (Orange)
    if selected_fire_metric == "Burned Area":
        fig.add_trace(
            go.Scatter(
                x=fire_df["Year"],
                y=fire_df["Burned Area (ha)"],
                mode="lines+markers",
                name="Burned Area (ha)",
                line=dict(color="orange", dash="dot"),
                marker=dict(color="orange", size=6),
                yaxis="y3",
            )
        )

    # ✅ Layout Adjustments
    fig.update_layout(
        width=600, height=600,
        xaxis=dict(title="Year", tickangle=-45, tickfont=dict(size=14)),
        yaxis=dict(title="Number of Permits", gridcolor="lightgray"),  # Primary Y-Axis
        yaxis2=dict(
            title=dict(text="Number of Fires", font=dict(color="red")),  # ✅ Corrected title font setting
            overlaying="y",
            side="right",
            showgrid=False,
            tickfont=dict(color="red"),  # ✅ Red axis numbers
        ),
        yaxis3=dict(
            title=dict(text="Burned Area (ha)", font=dict(color="orange")),  # ✅ Corrected title font setting
            overlaying="y",
            side="right",
            showgrid=False,
            tickfont=dict(color="orange"),  # ✅ Orange axis numbers
            anchor="free",
            position=1,
        ),
        plot_bgcolor="white",
        showlegend=True,
        legend=dict(x=1.1),  # ✅ Move legend box more to the right
    )

    return fig


def plot_technology_growth(df, fire_df, selected_fire_metric):
    """Stacked area chart of technology trends over time with user-selected fire data."""

    df["Year"] = df["Application Submission Date"].dt.year
    tech_trends = df.groupby(["Year", "Technology"])["Installed Capacity (MW)"].sum().reset_index()

    fig = go.Figure()

    # ✅ Primary Y-Axis: Installed Capacity (Blue)
    for tech in tech_trends["Technology"].unique():
        tech_data = tech_trends[tech_trends["Technology"] == tech]
        fig.add_trace(
            go.Scatter(
                x=tech_data["Year"],
                y=tech_data["Installed Capacity (MW)"],
                mode="lines",
                stackgroup="one",
                name=tech,
                line=dict(width=2),
                fill="tonexty",
                yaxis="y1",
            )
        )

    # ✅ Secondary Y-Axis: Number of Fires (Red)
    if selected_fire_metric == "Number of Fires":
        fig.add_trace(
            go.Scatter(
                x=fire_df["Year"],
                y=fire_df["Number of Fires"],
                mode="lines+markers",
                name="Number of Fires",
                line=dict(color="red", dash="dash"),
                marker=dict(color="red", size=6),
                yaxis="y2",
            )
        )

    # ✅ Tertiary Y-Axis: Burned Area (Orange)
    if selected_fire_metric == "Burned Area":
        fig.add_trace(
            go.Scatter(
                x=fire_df["Year"],
                y=fire_df["Burned Area (ha)"],
                mode="lines+markers",
                name="Burned Area (ha)",
                line=dict(color="orange", dash="dot"),
                marker=dict(color="orange", size=6),
                yaxis="y3",
            )
        )

    # ✅ Layout Adjustments
    fig.update_layout(
        width=600, height=600,
        xaxis=dict(title="Year", tickangle=-45, tickfont=dict(size=14)),
        yaxis=dict(title="Installed Capacity (MW)", gridcolor="lightgray"),  # Primary Y-Axis
        yaxis2=dict(
            title=dict(text="Number of Fires", font=dict(color="red")),  # ✅ Corrected title font setting
            overlaying="y",
            side="right",
            showgrid=False,
            tickfont=dict(color="red"),  # ✅ Red axis numbers
        ),
        yaxis3=dict(
            title=dict(text="Burned Area (ha)", font=dict(color="orange")),  # ✅ Corrected title font setting
            overlaying="y",
            side="right",
            showgrid=False,
            tickfont=dict(color="orange"),  # ✅ Orange axis numbers
            anchor="free",
            position=1,
        ),
        plot_bgcolor="white",
        showlegend=True,
        legend=dict(x=1.1),  # ✅ Move legend box more to the right
    )

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
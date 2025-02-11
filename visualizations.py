import streamlit as st
import plotly.express as px
import folium
import geopandas as gpd
from streamlit_folium import folium_static


def plot_permit_distribution(df):
    """Bar chart of permits per region."""
    permit_counts = df["ΠΕΡΙΦΕΡΕΙΑ"].value_counts().reset_index()
    permit_counts.columns = ["Περιοχή", "Αριθμός Αδειών"]

    fig = px.bar(permit_counts, x="Περιοχή", y="Αριθμός Αδειών",
                 title="Κατανομή Αδειών Ανανεώσιμων Πηγών Ενέργειας ανά Περιφέρεια")

    fig.update_layout(
        width=600,  # Set width equal to height for square aspect ratio
        height=800
    )
    return fig


def plot_installed_capacity(df):
    """Pie chart of installed MW per technology."""
    capacity = df.groupby("ΤΕΧΝΟΛΟΓΙΑ")["ΜΕΓΙΣΤΗ ΙΣΧΥΣ (MW)"].sum().reset_index()

    fig = px.pie(capacity, values="ΜΕΓΙΣΤΗ ΙΣΧΥΣ (MW)", names="ΤΕΧΝΟΛΟΓΙΑ",
                 title="Κατανομή Ισχύος (MW) ανά Τεχνολογία")

    fig.update_layout(
        width=600,  # Set width equal to height for square aspect ratio
        height=600
    )
    return fig


def create_folium_map(df):
    """Create an interactive Folium map of permits by region."""
    greece_map = folium.Map(location=[38.0, 23.7], zoom_start=6)

    # Aggregate permit count by region
    permit_counts = df.groupby("ΠΕΡΙΦΕΡΕΙΑ").size().reset_index()
    permit_counts.columns = ["Περιοχή", "Αριθμός Αδειών"]

    for _, row in permit_counts.iterrows():
        folium.Marker(
            location=[38.0, 23.7],  # Dummy coordinates (Replace with actual)
            popup=f"{row['Περιοχή']}: {row['Αριθμός Αδειών']} άδειες",
            icon=folium.Icon(color="blue"),
        ).add_to(greece_map)

    return greece_map


def plot_permits_over_time(df):
    """Line chart of permits issued over time."""
    df["Year"] = df["ΗΜΕΡΟΜΗΝΙΑ ΥΠΟΒΟΛΗΣ ΑΙΤΗΣΗΣ"].dt.year
    permits_per_year = df.groupby("Year").size().reset_index(name="Αριθμός Αδειών")

    fig = px.line(
        permits_per_year, x="Year", y="Αριθμός Αδειών",
        title="📈 Εξέλιξη Αδειών Ανανεώσιμων Πηγών Ενέργειας",
        markers=True
    )

    fig.update_layout(width=600, height=600)  # Square aspect ratio
    return fig


def plot_technology_growth(df):
    """Stacked area chart showing technology trends over time."""
    df["Year"] = df["ΗΜΕΡΟΜΗΝΙΑ ΥΠΟΒΟΛΗΣ ΑΙΤΗΣΗΣ"].dt.year
    tech_trends = df.groupby(["Year", "ΤΕΧΝΟΛΟΓΙΑ"])["ΜΕΓΙΣΤΗ ΙΣΧΥΣ (MW)"].sum().reset_index()

    fig = px.area(
        tech_trends, x="Year", y="ΜΕΓΙΣΤΗ ΙΣΧΥΣ (MW)", color="ΤΕΧΝΟΛΟΓΙΑ",
        title="📊 Ανάπτυξη Τεχνολογιών ΑΠΕ με την Πάροδο του Χρόνου",
        line_group="ΤΕΧΝΟΛΟΓΙΑ"
    )

    fig.update_layout(width=600, height=600)  # Square aspect ratio
    return fig


def plot_top_permits(df):
    """Bar chart of the top 10 largest permits."""
    top_permits = df.nlargest(10, "ΜΕΓΙΣΤΗ ΙΣΧΥΣ (MW)")

    fig = px.bar(
        top_permits, x="ΜΕΓΙΣΤΗ ΙΣΧΥΣ (MW)", y="ΑΡΙΘΜΟΣ ΜΗΤΡΩΟΥ ΑΔΕΙΩΝ",
        title="🔝 Οι 10 Μεγαλύτερες Άδειες ΑΠΕ",
        orientation='h'
    )

    fig.update_layout(width=600, height=600)  # Square aspect ratio
    return fig



def plot_energy_mix_per_region(df):
    """Sunburst chart of energy mix per region."""
    fig = px.sunburst(
        df, path=["ΠΕΡΙΦΕΡΕΙΑ", "ΤΕΧΝΟΛΟΓΙΑ"], values="ΜΕΓΙΣΤΗ ΙΣΧΥΣ (MW)",
        title="🌞 Ενεργειακό Μείγμα Ανά Περιφέρεια και Τεχνολογία"
    )

    fig.update_layout(width=600, height=600)  # Square aspect ratio
    return fig


def plot_expiring_permits(df):
    """Histogram of expiring permits per year."""
    df["Year"] = df["ΗΜΕΡΟΜΗΝΙΑ ΛΗΞΗΣ ΑΔ.ΠΑΡΑΓΩΓΗΣ"].dt.year
    expiration_counts = df["Year"].value_counts().reset_index()
    expiration_counts.columns = ["Year", "Αριθμός Αδειών"]

    fig = px.bar(
        expiration_counts, x="Year", y="Αριθμός Αδειών",
        title="⏳ Λήξεις Αδειών Ανανεώσιμων Πηγών Ενέργειας",
    )

    fig.update_layout(width=600, height=600)  # Square aspect ratio
    return fig

from flask import Flask, jsonify
import sys
import os
import pandas as pd
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from data_loader import load_data  # ✅ Load your existing data

from flask_cors import CORS # just in case...
app = Flask(__name__)
CORS(app)


app = Flask(__name__)

# Load the dataset (processed permits data)
df = load_data()


@app.route("/")
def home():
    """Basic API Home Route"""
    return jsonify({"message": "Renewable Energy Permits API"})


# ✅ GENERAL DATA ENDPOINTS (only fyi)
@app.route("/permits", methods=["GET"])
def get_permits():
    """Returns all permits"""
    return jsonify(df.to_dict(orient="records"))


@app.route("/permit/<permit_id>", methods=["GET"])
def get_permit(permit_id):
    """Returns a specific permit by ID"""
    permit = df[df["Permit ID"] == permit_id]
    if permit.empty:
        return jsonify({"error": "Permit not found"}), 404
    return jsonify(permit.to_dict(orient="records")[0])


@app.route("/permits/region/<region>", methods=["GET"])
def get_permits_by_region(region):
    """Returns permits for a specific region"""
    filtered_df = df[df["Region"].str.lower() == region.lower()]
    if filtered_df.empty:
        return jsonify({"error": "No permits found in this region"}), 404
    return jsonify(filtered_df.to_dict(orient="records"))






######################### THIS IS WHERE DATA FOR EACH VISUALIZATION STARTS #########################

# ✅ VISUALIZATION ENDPOINTS (Data Analysis tab)

@app.route("/visualization/permit_distribution", methods=["GET"])
def get_permit_distribution():
    """Returns data for Permit Distribution visualization"""
    permit_counts = df.groupby(["Region", "Technology"]).size().reset_index(name="Number of Permits")
    return jsonify(permit_counts.to_dict(orient="records"))


@app.route("/visualization/permits_over_time", methods=["GET"])
def get_permits_over_time():
    """Returns data for Permit Trends Over Time visualization"""
    df["Year"] = df["Application Submission Date"].dt.year
    permits_per_year = df.groupby("Year").size().reset_index(name="Number of Permits")
    return jsonify(permits_per_year.to_dict(orient="records"))


@app.route("/visualization/technology_growth", methods=["GET"])
def get_technology_growth():
    """Returns data for Growth of Renewable Technologies"""
    df["Year"] = df["Application Submission Date"].dt.year
    tech_trends = df.groupby(["Year", "Technology"])["Installed Capacity (MW)"].sum().reset_index()
    return jsonify(tech_trends.to_dict(orient="records"))


@app.route("/visualization/installed_capacity", methods=["GET"])
def get_installed_capacity():
    """Returns data for Installed Capacity by Technology"""
    capacity = df.groupby("Technology")["Installed Capacity (MW)"].sum().reset_index()
    return jsonify(capacity.to_dict(orient="records"))


@app.route("/visualization/top_permits", methods=["GET"])
def get_top_permits():
    """Returns data for Top 10 Largest Permits"""
    top_permits = df.nlargest(10, "Installed Capacity (MW)")[["Permit ID", "Company", "Installed Capacity (MW)", "Technology"]]
    return jsonify(top_permits.to_dict(orient="records"))


@app.route("/visualization/energy_mix", methods=["GET"])
def get_energy_mix():
    """Returns data for Energy Mix by Region"""
    energy_mix = df.groupby(["Region", "Technology"])["Installed Capacity (MW)"].sum().reset_index()
    return jsonify(energy_mix.to_dict(orient="records"))


@app.route("/visualization/expiring_permits", methods=["GET"])
def get_expiring_permits():
    """Returns data for Expiring Permits Timeline"""
    df["Year"] = df["Permit Expiration Date"].dt.year
    expiration_counts = df.groupby(["Year", "Technology"]).size().reset_index(name="Number of Permits")
    return jsonify(expiration_counts.to_dict(orient="records"))


@app.route("/visualization/cumulative_installed_capacity", methods=["GET"])
def get_cumulative_installed_capacity():
    """Returns data for Cumulative Installed Capacity Over Time (Total & Per Technology)"""
    df["Year"] = df["Permit Issuance Date"].dt.year

    # ✅ Compute the total cumulative sum over time
    total_capacity = df.groupby("Year")["Installed Capacity (MW)"].sum().cumsum().reset_index()
    total_capacity["Technology"] = "Total"  # Add label for total

    # ✅ Compute cumulative installed capacity per technology
    tech_capacity = df.groupby(["Year", "Technology"])["Installed Capacity (MW)"].sum().groupby(level=1).cumsum().reset_index()

    # ✅ Combine total and per-technology cumulative capacity
    combined_capacity = pd.concat([total_capacity, tech_capacity], ignore_index=True)

    return jsonify(combined_capacity.to_dict(orient="records"))


@app.route("/visualization/permit_type_distribution", methods=["GET"])
def get_permit_type_distribution():
    """Returns data for Permit Type Distribution Over Time"""
    df["Year"] = df["Application Submission Date"].dt.year
    permit_trends = df.groupby(["Year", "Technology"]).size().reset_index(name="Number of Permits")
    return jsonify(permit_trends.to_dict(orient="records"))


@app.route("/visualization/sankey_permits", methods=["GET"])
def get_sankey_permits():
    """Returns data for Sankey Diagram of Permits Flow"""
    permit_counts = df.groupby(["Region", "Technology"]).size().reset_index(name="Number of Permits")
    return jsonify(permit_counts.to_dict(orient="records"))


@app.route("/visualization/processing_time", methods=["GET"])
def get_processing_time():
    """Returns data for Permit Processing Time Analysis"""
    df["Processing Time (Days)"] = (df["Permit Issuance Date"] - df["Application Submission Date"]).dt.days
    df["Year"] = df["Application Submission Date"].dt.year
    processing_time_trends = df.groupby("Year")["Processing Time (Days)"].mean().reset_index()
    return jsonify(processing_time_trends.to_dict(orient="records"))


@app.route("/visualization/violin_processing_time", methods=["GET"])
def get_violin_processing_time():
    """Returns data for Violin Plot of Permit Processing Time by Technology"""

    global df  # Ensure we're using the global DataFrame

    # ✅ Make a copy of df before modifying to avoid global modification issues
    df_filtered = df.copy()

    # ✅ Compute processing time in days
    df_filtered["Processing Time (Days)"] = (
            df_filtered["Permit Issuance Date"] - df_filtered["Application Submission Date"]
    ).dt.days

    # ✅ Remove invalid (negative or missing) processing times
    df_filtered = df_filtered[df_filtered["Processing Time (Days)"] > 0]

    # ✅ Convert to dictionary format (list of values per Technology)
    violin_data = df_filtered.groupby("Technology")["Processing Time (Days)"].apply(list).to_dict()

    return jsonify(violin_data)





# ✅ VISUALIZATION ENDPOINTS (Map tab)

@app.route("/geojson/regions", methods=["GET"])
def get_regions_geojson():
    """Returns the GeoJSON for Greece's administrative regions."""
    geojson_path = "data/geo/greece-regions.geojson"
    try:
        with open(geojson_path, "r", encoding="utf-8") as f:
            return jsonify(json.load(f))  # Serve as JSON response
    except Exception as e:
        return jsonify({"error": f"Could not load GeoJSON: {str(e)}"}), 500


@app.route("/geojson/regional_units", methods=["GET"])
def get_regional_units_geojson():
    """Returns the GeoJSON for Greece's regional units (prefectures)."""
    geojson_path = "data/geo/greece-prefectures.geojson"
    try:
        with open(geojson_path, "r", encoding="utf-8") as f:
            return jsonify(json.load(f))  # Serve as JSON response
    except Exception as e:
        return jsonify({"error": f"Could not load GeoJSON: {str(e)}"}), 500


@app.route("/map/permits", methods=["GET"])
def get_map_permits():
    """Returns JSON data for mapping permits (Regions & Regional Units)."""

    global df

    # Remove rows where LAT or LON is NaN for REGIONS (we are basically not mapping them in this case)
    df_regions = df.dropna(subset=["LAT", "LON"])

    # Remove rows where LAT_UNIT or LON_UNIT is NaN for REGIONAL UNITS (same here)
    df_units = df.dropna(subset=["LAT_UNIT", "LON_UNIT"])

    # Get Regions Data
    regions_data = get_map_regions(df_regions)

    # Get Regional Units Data
    units_data = get_map_regional_units(df_units)

    return jsonify({
        "regions": regions_data,
        "regional_units": units_data
    })


### **🔷 Separate Function for Regions**
def get_map_regions(df_regions):
    """Processes and returns Region-level permit data."""

    # Aggregate data by Region
    region_summary = df_regions.groupby("Region").agg({
        "Permit ID": "count",
        "Installed Capacity (MW)": "sum"
    }).reset_index()

    # Get technology breakdown for each region
    region_tech_breakdown = df_regions.groupby(["Region", "Technology"])["Installed Capacity (MW)"].sum().reset_index()

    region_data = []
    for _, row in region_summary.iterrows():
        region = row["Region"]
        total_permits = int(row["Permit ID"])
        total_capacity = float(row["Installed Capacity (MW)"])

        # Get technology breakdown for this region
        tech_data = region_tech_breakdown[region_tech_breakdown["Region"] == region]
        tech_breakdown = {tech: round(capacity, 2) for tech, capacity in
                          zip(tech_data["Technology"], tech_data["Installed Capacity (MW)"])}

        # Find latitude & longitude (guaranteed not NaN)
        lat, lon = df_regions[df_regions["Region"] == region].iloc[0][["LAT", "LON"]]

        region_data.append({
            "region": region,
            "total_permits": total_permits,
            "total_capacity_mw": total_capacity,
            "technology_breakdown": tech_breakdown,
            "lat": lat,
            "lon": lon
        })

    return region_data


### **🔷 Separate Function for Regional Units**
def get_map_regional_units(df_units):
    """Processes and returns Regional Unit-level permit data."""

    # Aggregate data by Regional Unit
    unit_summary = df_units.groupby("Regional Unit").agg({
        "Permit ID": "count",
        "Installed Capacity (MW)": "sum"
    }).reset_index()

    # Get technology breakdown for each Regional Unit
    unit_tech_breakdown = df_units.groupby(["Regional Unit", "Technology"])["Installed Capacity (MW)"].sum().reset_index()

    unit_data = []
    for _, row in unit_summary.iterrows():
        unit = row["Regional Unit"]
        total_permits = int(row["Permit ID"])
        total_capacity = float(row["Installed Capacity (MW)"])

        # Get technology breakdown for this unit
        tech_data = unit_tech_breakdown[unit_tech_breakdown["Regional Unit"] == unit]
        tech_breakdown = {tech: round(capacity, 2) for tech, capacity in
                          zip(tech_data["Technology"], tech_data["Installed Capacity (MW)"])}

        # Find latitude & longitude (guaranteed not NaN)
        lat, lon = df_units[df_units["Regional Unit"] == unit].iloc[0][["LAT_UNIT", "LON_UNIT"]]

        unit_data.append({
            "regional_unit": unit,
            "total_permits": total_permits,
            "total_capacity_mw": total_capacity,
            "technology_breakdown": tech_breakdown,
            "lat": lat,
            "lon": lon
        })

    return unit_data



# ✅ VISUALIZATION ENDPOINTS (Data Table tab)
@app.route("/data/table", methods=["GET"])
def get_data_table():
    """Returns the dataset for the Data Table tab, excluding unnecessary columns."""

    # Define columns to drop
    columns_to_drop = ["Year", "LAT", "LON", "LAT_UNIT", "LON_UNIT", "Processing Time (Days)"]

    # Ensure only existing columns are dropped
    df_display = df.drop(columns=[col for col in columns_to_drop if col in df.columns], errors="ignore")

    # Convert to JSON and return
    return jsonify(df_display.to_dict(orient="records"))


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)

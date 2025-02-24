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


# Load the dataset (processed permits data)
df = load_data()


@app.route("/")
def home():
    """
    Home Route
    ---
    responses:
      200:
        description: Welcome message
        examples:
          application/json: { "message": "Renewable Energy Permits API" }
    """
    return jsonify({"message": "Renewable Energy Permits API"})


@app.route("/geojson/regions", methods=["GET"])
def get_regions_geojson():
    geojson_path = os.path.join("data", "geo", "greece-regions.geojson")
    try:
        with open(geojson_path, "r", encoding="utf-8") as f:
            return jsonify(json.load(f))
    except Exception as e:
        return jsonify({"error": f"Could not load GeoJSON: {str(e)}"}), 500

@app.route("/geojson/regional_units", methods=["GET"])
def get_regional_units_geojson():
    geojson_path = os.path.join("data", "geo", "greece-prefectures.geojson")
    try:
        with open(geojson_path, "r", encoding="utf-8") as f:
            return jsonify(json.load(f))
    except Exception as e:
        return jsonify({"error": f"Could not load GeoJSON: {str(e)}"}), 500


######################### THIS IS WHERE DATA FOR EACH VISUALIZATION STARTS #########################

# ✅ VISUALIZATION ENDPOINTS (Data Analysis tab)

@app.route("/visualization/permit_distribution", methods=["GET"])
def get_permit_distribution():
    """
    Get Permit Distribution Data
    ---
    visualization_type: Stacked Bar Chart
    description: Returns the distribution of permits across regions and technologies. Ideal for a stacked bar chart where each region's bar is segmented by technology.
    responses:
      200:
        description: Data for permit distribution visualization
        schema:
          type: array
          items:
            type: object
            properties:
              Region:
                type: string
                example: "Attica"
              Technology:
                type: string
                example: "Solar"
              Number of Permits:
                type: integer
                example: 25
        examples:
          application/json: [
            { "Region": "Attica", "Technology": "Solar", "Number of Permits": 25 },
            { "Region": "Crete", "Technology": "Wind", "Number of Permits": 18 }
          ]
    """

    permit_counts = df.groupby(["Region", "Technology"]).size().reset_index(name="Number of Permits")
    return jsonify(permit_counts.to_dict(orient="records"))



@app.route("/visualization/permits_over_time", methods=["GET"])
def get_permits_over_time():
    """
    Get Permits Over Time
    ---
    visualization_type: Line Chart
    description: Returns the total number of permits issued over time. Useful for visualizing temporal trends in permit issuance as a line chart.
    responses:
      200:
        description: Number of permits issued over the years
        schema:
          type: array
          items:
            type: object
            properties:
              Year:
                type: integer
                example: 2020
              Number of Permits:
                type: integer
                example: 45
        examples:
          application/json: [
            { "Year": 2020, "Number of Permits": 45 },
            { "Year": 2021, "Number of Permits": 58 }
          ]
    """

    df["Year"] = df["Application Submission Date"].dt.year
    permits_per_year = df.groupby("Year").size().reset_index(name="Number of Permits")
    return jsonify(permits_per_year.to_dict(orient="records"))


@app.route("/visualization/technology_growth", methods=["GET"])
def get_technology_growth():
    """
    Get Technology Growth Over Time
    ---
    visualization_type: Stacked Area Chart
    description: Shows the growth of installed capacity (in MW) over time, broken down by renewable technology. Visualized as a stacked area chart.
    responses:
      200:
        description: Growth of renewable technologies over time
        schema:
          type: array
          items:
            type: object
            properties:
              Year:
                type: integer
                example: 2021
              Technology:
                type: string
                example: "Wind"
              Installed Capacity (MW):
                type: number
                example: 150.5
        examples:
          application/json: [
            { "Year": 2020, "Technology": "Solar", "Installed Capacity (MW)": 120.3 },
            { "Year": 2020, "Technology": "Wind", "Installed Capacity (MW)": 150.5 }
          ]
    """
    df["Year"] = df["Application Submission Date"].dt.year
    tech_trends = df.groupby(["Year", "Technology"])["Installed Capacity (MW)"].sum().reset_index()
    return jsonify(tech_trends.to_dict(orient="records"))


@app.route("/visualization/installed_capacity", methods=["GET"])
def get_installed_capacity():
    """
    Get Installed Capacity by Technology
    ---
    visualization_type: Pie Chart
    description: Provides the total installed capacity (in MW) for each technology. Suitable for a pie chart showing the proportion of each technology.
    responses:
      200:
        description: Installed capacity per technology
        schema:
          type: array
          items:
            type: object
            properties:
              Technology:
                type: string
                example: "Solar"
              Installed Capacity (MW):
                type: number
                example: 450.7
        examples:
          application/json: [
            { "Technology": "Solar", "Installed Capacity (MW)": 450.7 },
            { "Technology": "Wind", "Installed Capacity (MW)": 380.2 }
          ]
    """
    capacity = df.groupby("Technology")["Installed Capacity (MW)"].sum().reset_index()
    return jsonify(capacity.to_dict(orient="records"))


@app.route("/visualization/top_permits", methods=["GET"])
def get_top_permits():
    """
    Get Top 10 Largest Permits
    ---
    visualization_type: Horizontal Bar Chart
    description: Returns the top 10 largest permits based on installed capacity. Perfect for a horizontal bar chart.
    responses:
      200:
        description: Top 10 permits by installed capacity
        schema:
          type: array
          items:
            type: object
            properties:
              Permit ID:
                type: string
                example: "PERMIT12345"
              Company:
                type: string
                example: "Green Energy Inc."
              Installed Capacity (MW):
                type: number
                example: 300.5
              Technology:
                type: string
                example: "Wind"
        examples:
          application/json: [
            { "Permit ID": "PERMIT12345", "Company": "Green Energy Inc.", "Installed Capacity (MW)": 300.5, "Technology": "Wind" },
            { "Permit ID": "PERMIT67890", "Company": "Solar Solutions", "Installed Capacity (MW)": 280.3, "Technology": "Solar" }
          ]
    """
    top_permits = df.nlargest(10, "Installed Capacity (MW)")[["Permit ID", "Company", "Installed Capacity (MW)", "Technology"]]
    return jsonify(top_permits.to_dict(orient="records"))


@app.route("/visualization/energy_mix", methods=["GET"])
def get_energy_mix():
    """
    Get Energy Mix by Region
    ---
    visualization_type: Sunburst Chart
    description: Shows the energy mix breakdown by region and technology. Suitable for a sunburst chart or treemap.
    responses:
      200:
        description: Energy mix breakdown by region and technology
        schema:
          type: array
          items:
            type: object
            properties:
              Region:
                type: string
                example: "Crete"
              Technology:
                type: string
                example: "Solar"
              Installed Capacity (MW):
                type: number
                example: 250.0
        examples:
          application/json: [
            { "Region": "Crete", "Technology": "Solar", "Installed Capacity (MW)": 250.0 },
            { "Region": "Attica", "Technology": "Wind", "Installed Capacity (MW)": 400.5 }
          ]
    """
    energy_mix = df.groupby(["Region", "Technology"])["Installed Capacity (MW)"].sum().reset_index()
    return jsonify(energy_mix.to_dict(orient="records"))


@app.route("/visualization/expiring_permits", methods=["GET"])
def get_expiring_permits():
    """
    Get Expiring Permits Timeline
    ---
    visualization_type: Stacked Bar Chart
    description: Displays the number of permits expiring over time, broken down by technology. Ideal for a stacked bar chart.
    responses:
      200:
        description: Number of permits expiring over time
        schema:
          type: array
          items:
            type: object
            properties:
              Year:
                type: integer
                example: 2025
              Technology:
                type: string
                example: "Biomass"
              Number of Permits:
                type: integer
                example: 15
        examples:
          application/json: [
            { "Year": 2025, "Technology": "Biomass", "Number of Permits": 15 },
            { "Year": 2026, "Technology": "Solar", "Number of Permits": 20 }
          ]
    """
    df["Year"] = df["Permit Expiration Date"].dt.year
    expiration_counts = df.groupby(["Year", "Technology"]).size().reset_index(name="Number of Permits")
    return jsonify(expiration_counts.to_dict(orient="records"))


@app.route("/visualization/cumulative_installed_capacity", methods=["GET"])
def get_cumulative_installed_capacity():
    """
    Get Cumulative Installed Capacity
    ---
    visualization_type: Line Chart
    description: Shows cumulative installed capacity over time, both overall and by technology. Suitable for a multi-line chart.
    responses:
      200:
        description: Cumulative installed capacity over time
        schema:
          type: array
          items:
            type: object
            properties:
              Year:
                type: integer
                example: 2024
              Installed Capacity (MW):
                type: number
                example: 1200.0
              Technology:
                type: string
                example: "Total"
        examples:
          application/json: [
            { "Year": 2024, "Installed Capacity (MW)": 1200.0, "Technology": "Total" },
            { "Year": 2024, "Installed Capacity (MW)": 800.0, "Technology": "Solar" }
          ]
    """
    df["Year"] = df["Permit Issuance Date"].dt.year
    total_capacity = df.groupby("Year")["Installed Capacity (MW)"].sum().cumsum().reset_index()
    total_capacity["Technology"] = "Total"
    tech_capacity = df.groupby(["Year", "Technology"])["Installed Capacity (MW)"].sum().groupby(level=1).cumsum().reset_index()
    combined_capacity = pd.concat([total_capacity, tech_capacity], ignore_index=True)
    return jsonify(combined_capacity.to_dict(orient="records"))


@app.route("/visualization/permit_type_distribution", methods=["GET"])
def get_permit_type_distribution():
    """
    Get Permit Type Distribution Over Time
    ---
    visualization_type: Stacked Area Chart
    description: Displays the distribution of permit types over time, segmented by technology. Best shown as a stacked area chart.
    responses:
      200:
        description: Permit distribution by type over time
        schema:
          type: array
          items:
            type: object
            properties:
              Year:
                type: integer
                example: 2022
              Technology:
                type: string
                example: "Wind"
              Number of Permits:
                type: integer
                example: 40
        examples:
          application/json: [
            { "Year": 2022, "Technology": "Wind", "Number of Permits": 40 },
            { "Year": 2023, "Technology": "Solar", "Number of Permits": 35 }
          ]
    """
    df["Year"] = df["Application Submission Date"].dt.year
    permit_trends = df.groupby(["Year", "Technology"]).size().reset_index(name="Number of Permits")
    return jsonify(permit_trends.to_dict(orient="records"))


@app.route("/visualization/sankey_permits", methods=["GET"])
def get_sankey_permits():
    """
    Get Sankey Diagram Data
    ---
    visualization_type: Sankey Diagram
    description: Returns data structured for creating a Sankey diagram showing permit flow between regions and technologies.
    responses:
      200:
        description: Sankey diagram data
        schema:
          type: array
          items:
            type: object
            properties:
              Region:
                type: string
              Technology:
                type: string
              Number of Permits:
                type: integer
    """
    permit_counts = df.groupby(["Region", "Technology"]).size().reset_index(name="Number of Permits")
    return jsonify(permit_counts.to_dict(orient="records"))



@app.route("/visualization/processing_time", methods=["GET"])
def get_processing_time():
    """
    Get Permit Processing Time
    ---
    responses:
      200:
        description: Average permit processing time per year
        schema:
          type: array
          items:
            type: object
            properties:
              Year:
                type: integer
              Processing Time (Days):
                type: number
    """
    df["Processing Time (Days)"] = (df["Permit Issuance Date"] - df["Application Submission Date"]).dt.days
    df["Year"] = df["Application Submission Date"].dt.year
    processing_time_trends = df.groupby("Year")["Processing Time (Days)"].mean().reset_index()
    return jsonify(processing_time_trends.to_dict(orient="records"))


@app.route("/visualization/violin_processing_time", methods=["GET"])
def get_violin_processing_time():
    """
    Get Violin Plot Data for Processing Time
    ---
    visualization_type: Violin Plot
    description: Provides the distribution of permit processing times per technology. Ideal for a violin plot.
    responses:
      200:
        description: Distribution of processing times by technology
        schema:
          type: object
          additionalProperties:
            type: array
            items:
              type: number
        examples:
          application/json: {
            "Solar": [30, 45, 50, 60],
            "Wind": [25, 40, 55, 70]
          }
    """
    df_filtered = df.copy()
    df_filtered["Processing Time (Days)"] = (df_filtered["Permit Issuance Date"] - df_filtered["Application Submission Date"]).dt.days
    df_filtered = df_filtered[df_filtered["Processing Time (Days)"] > 0]
    violin_data = df_filtered.groupby("Technology")["Processing Time (Days)"].apply(list).to_dict()
    return jsonify(violin_data)



def get_map_regions(df_regions):
    """Processes and returns Region-level permit data."""
    region_summary = df_regions.groupby("Region").agg({
        "Permit ID": "count",
        "Installed Capacity (MW)": "sum"
    }).reset_index()

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


def get_map_regional_units(df_units):
    """Processes and returns Regional Unit-level permit data."""
    unit_summary = df_units.groupby("Regional Unit").agg({
        "Permit ID": "count",
        "Installed Capacity (MW)": "sum"
    }).reset_index()

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



@app.route("/map/permits", methods=["GET"])
def get_map_permits():
    """
    Get Permit Data for Mapping
    ---
    visualization_type: Map with Markers
    description: Returns JSON data for mapping permits, including coordinates for both regions and regional units.
    responses:
      200:
        description: JSON data for permits mapping
        examples:
          application/json: {
            "regions": [
              { "region": "Attica", "total_permits": 50, "total_capacity_mw": 500.0, "lat": 38.0, "lon": 23.7, "technology_breakdown": {"Solar": 300.0, "Wind": 200.0} }
            ],
            "regional_units": [
              { "regional_unit": "Piraeus", "total_permits": 20, "total_capacity_mw": 200.0, "lat": 37.9, "lon": 23.6, "technology_breakdown": {"Solar": 150.0} }
            ]
          }
    """
    global df

    df_regions = df.dropna(subset=["LAT", "LON"])
    df_units = df.dropna(subset=["LAT_UNIT", "LON_UNIT"])

    regions_data = get_map_regions(df_regions)
    units_data = get_map_regional_units(df_units)

    return jsonify({
        "regions": regions_data,
        "regional_units": units_data
    })


# ✅ VISUALIZATION ENDPOINTS (Data Table tab)

@app.route("/data/table", methods=["GET"])
def get_data_table():
    """
    Get Full Permits Data Table
    ---
    visualization_type: Data Table
    description: Returns the entire dataset for the permits, excluding unnecessary columns, suitable for rendering as a searchable/sortable table.
    responses:
      200:
        description: Full permits data
        examples:
          application/json: [
            { "Permit ID": "PERMIT12345", "Region": "Attica", "Technology": "Solar", "Installed Capacity (MW)": 300.5, "Application Submission Date": "2020-05-20" },
            { "Permit ID": "PERMIT67890", "Region": "Crete", "Technology": "Wind", "Installed Capacity (MW)": 400.0, "Application Submission Date": "2021-06-15" }
          ]
    """
    columns_to_drop = ["Year", "LAT", "LON", "LAT_UNIT", "LON_UNIT", "Processing Time (Days)"]
    df_display = df.drop(columns=[col for col in columns_to_drop if col in df.columns], errors="ignore")
    return jsonify(df_display.to_dict(orient="records"))

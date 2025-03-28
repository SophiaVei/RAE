import streamlit as st  # ✅ Move st.set_page_config to the top before anything else
st.set_page_config(page_title="Renewable Energy Permits in Greece", layout="wide")  # ✅ Must be first!

import pandas as pd
from data_loader import load_data
from greece_map import create_combined_map, create_prefecture_map
from streamlit_folium import st_folium
from visualizations import (
    plot_permit_distribution,
    plot_installed_capacity,  # ✅ Re-added the missing plot
    plot_permits_over_time,
    plot_technology_growth,
    plot_top_permits,
    plot_energy_mix_per_region,
    plot_expiring_permits,
    plot_cumulative_installed_capacity,
    plot_permit_processing_time,
    plot_permit_type_distribution,
    plot_sankey_permits,
    plot_violin_processing_time
)

# Load data
df = load_data()


# Dashboard Title
st.title("⚡ Renewable Energy Permits in Greece")

# Tabs for navigation
tab1, tab2, tab3 = st.tabs(["📊 Data Analysis", "🌍 Map", "🔍 Data Table"])

# ✅ **Tab 1: Data Analysis**
with tab1:
    # 📊 Permit Distribution
    st.subheader("📊 Permit Distribution")
    st.plotly_chart(plot_permit_distribution(df), use_container_width=True)

    st.markdown("""
    ℹ️ **How is this calculated?**  
    This stacked bar chart **aggregates the number of permits** issued in each region, categorized by **renewable energy technology**.

    📌 **What does it show?**  
    - The **distribution of permits across different regions**.
    - How **different renewable technologies** (e.g., wind, solar, biomass) are distributed.
    - Which regions are **leading** in renewable energy permit approvals.

    💡 **Why is it useful?**  
    - Identifies **regional trends** in renewable energy adoption.
    - Highlights **technology preferences** in different areas.
    - Provides insights into where **new investments** are being made.
    """)

    # 📈 Permit Trends Over Time
    st.subheader("📈 Permit Trends Over Time")
    st.plotly_chart(plot_permits_over_time(df), use_container_width=True)
    st.markdown("""
    ℹ️ **How is this calculated?**  
    This **line chart** shows the total number of permits issued each year.

    📌 **What does it show?**  
    - The **growth or decline** of permit approvals over time.
    - **Policy shifts** that may have influenced renewable energy permits.

    💡 **Why is it useful?**  
    - Helps track **historical patterns** in permit approvals.
    - Supports **policymaking** by showing when growth is accelerating or slowing.
    """)

    # 💡 Growth of Renewable Technologies
    st.subheader("💡 Growth of Renewable Technologies")
    st.plotly_chart(plot_technology_growth(df), use_container_width=True)

    st.markdown("""
    ℹ️ **How is this calculated?**  
    This **stacked area chart** tracks the installed capacity of each renewable energy technology **over time**.

    📌 **What does it show?**  
    - The **expansion of renewable technologies** such as wind, solar, and biomass.
    - Whether **certain technologies are growing faster** than others.
    - The impact of **policy changes** or economic conditions on technology adoption.

    💡 **Why is it useful?**  
    - Shows the **evolution of Greece's renewable energy landscape**.
    - Helps in **forecasting future trends** in energy production.
    - Identifies **which technologies are gaining traction**.
    """)

    # 💡 Installed Capacity by Technology
    st.subheader("💡 Installed Capacity by Technology")
    st.plotly_chart(plot_installed_capacity(df), use_container_width=True)

    st.markdown("""
    ℹ️ **How is this calculated?**  
    This **pie chart** represents the **total installed capacity (MW)** for each renewable technology.

    📌 **What does it show?**  
    - The **share of each technology** in Greece’s renewable energy sector.
    - Which **technologies dominate** in terms of installed capacity.
    - Potential **gaps in diversification**.

    💡 **Why is it useful?**  
    - Helps policymakers and investors understand **where resources are concentrated**.
    - Identifies whether Greece has a **balanced energy mix**.
    - Supports discussions on **future investments** in underrepresented technologies.
    """)

    # 🔝 Top 10 Largest Permits
    st.subheader("🔝 Top 10 Largest Permits")
    st.plotly_chart(plot_top_permits(df), use_container_width=True)

    st.markdown("""
    ℹ️ **How is this calculated?**  
    This **horizontal bar chart** shows the **top 10 permits** based on installed capacity (MW), categorized by technology.

    📌 **What does it show?**  
    - The **largest renewable energy projects** in Greece.
    - Which **technologies** have the **biggest projects**.
    - Which **companies or regions** are leading in large-scale installations.

    💡 **Why is it useful?**  
    - Highlights **key players** in the renewable energy sector.
    - Helps in identifying **investment trends**.
    - Provides insights into which regions are **home to major renewable projects**.
    """)

    # 🌞 Energy Mix by Region
    st.subheader("🌞 Energy Mix by Region")
    st.plotly_chart(plot_energy_mix_per_region(df), use_container_width=True)

    st.markdown("""
    ℹ️ **How is this calculated?**  
    This **sunburst chart** breaks down installed capacity by **region** and **technology type**.

    📌 **What does it show?**  
    - The **dominant energy sources** in different regions.
    - Which regions are more **diversified** in renewable energy.
    - If there are **regional preferences** for certain technologies.

    💡 **Why is it useful?**  
    - Helps **regional planners** make data-driven decisions.
    - Identifies areas where **certain technologies** are overrepresented or underrepresented.
    - Supports efforts to create a **more balanced energy mix**.
    """)

    # ⏳ Expiring Permits Timeline
    st.subheader("⏳ Expiring Permits Timeline")
    st.plotly_chart(plot_expiring_permits(df), use_container_width=True)
    st.markdown("""
    ℹ️ **How is this calculated?**  
    This **stacked bar chart** shows the number of permits that will expire each year, categorized by **technology**.

    📌 **What does it show?**  
    - When **major renewable energy projects** will need renewal.
    - Which **technologies** have the most upcoming expirations.
    - Whether Greece’s **renewable energy infrastructure** is aging.

    💡 **Why is it useful?**  
    - Helps **government agencies** and investors **prepare for renewals**.
    - Identifies periods where **a large number of permits expire**.
    - Supports **long-term energy planning**.
    """)

    # 📈 Cumulative Installed Capacity Over Time
    st.subheader("📈 Cumulative Installed Capacity Over Time")
    st.plotly_chart(plot_cumulative_installed_capacity(df), use_container_width=True)

    st.markdown("""
    ℹ️ **How is this calculated?**  
    This plot shows the **total installed capacity (MW) over time**, calculated by **summing** all permits issued up to each year.

    📌 **What does it show?**  
    It helps understand **how fast renewable energy installations are growing** in Greece.

    💡 **Why is it useful?**  
    - Identifies **periods of rapid growth or stagnation** in renewable energy development.
    - Helps **forecast future trends** based on historical data.
    """)

    # 💡 Permit Type Distribution Over Time
    st.subheader("💡 Permit Type Distribution Over Time")
    st.plotly_chart(plot_permit_type_distribution(df), use_container_width=True)

    st.markdown("""
    ℹ️ **How is this calculated?**  
    This **stacked area chart** shows the **number of permits issued** over time, categorized by technology.

    📌 **What does it show?**  
    - Which **renewable energy technologies** are seeing the most growth.
    - Whether **policy shifts** affected permit approvals.
    - Whether Greece is moving toward a **more diverse renewable energy mix**.
    """)

    st.subheader("🔄 Flow of Renewable Energy Permits")
    st.plotly_chart(plot_sankey_permits(df), use_container_width=True)

    st.markdown("""
    ℹ️ **How is this calculated?**  
    This Sankey diagram shows how **permits are distributed across regions and renewable technologies**.

    📌 **What does it show?**  
    - Which **regions** are issuing the most permits.
    - Which **technologies** are dominant in different regions.
    - Whether certain regions are **specialized** in a specific renewable energy source.

    💡 **Why is it useful?**  
    - Reveals potential **over-reliance** on certain technologies in specific areas.
    """)

    # 🕒 Permit Processing Time Analysis
    st.subheader("🕒 Permit Processing Time Analysis")
    st.plotly_chart(plot_permit_processing_time(df), use_container_width=True)

    st.markdown("""
        ℹ️ **How is this calculated?**  
        This **line chart** shows the **average time (days)** from **permit submission to issuance**.

        📌 **What does it show?**  
        - Whether **permit processing times** are improving or worsening.
        - How long companies and investors have to **wait for approvals**.
        - The impact of **policy changes** on efficiency.

        💡 **Why is it useful?**  
        - Helps **identify bureaucratic delays**.
        - Allows policymakers to set **faster approval targets**.
        - Supports companies in planning their **project timelines**.
        """)

    st.subheader("⏳ Permit Processing Time by Technology")
    st.plotly_chart(plot_violin_processing_time(df), use_container_width=True)

    st.markdown("""
    ℹ️ **How is this calculated?**  
    This violin plot visualizes the **distribution of processing times** (in days) for different **renewable energy technologies**.

    📌 **What does it show?**  
    - Which **technologies experience long processing delays**.
    - The **variability** in processing time.
    - Outliers where **permits took much longer or shorter** than expected.

    💡 **Why is it useful?**  
    - Helps policymakers identify **bottlenecks** in the approval process.
    - Supports **process optimization** for faster renewable energy growth.
    """)

# ✅ **Tab 2: Interactive Map**
with tab2:
    st.subheader("🌍 Map of Greece's Renewable Energy Permits")

    map_type = st.radio("Select Map Layer:", ["Regions", "Regional Units"])

    if map_type == "Regions":
        map_object = create_combined_map()
    else:
        map_object = create_prefecture_map()

    st_folium(map_object, use_container_width=True, height=900, key="combined_map")


# ✅ **Tab 3: Data Table**
with tab3:
    st.subheader("🔍 Data Table")

    # ✅ Drop unnecessary columns
    df_display = df.drop(
        columns=[
            "Year", "LAT", "LON", "LAT_UNIT", "LON_UNIT",
            "Processing Time (Days)", "Regional Unit", "Regional Unit Greek",
            "index_right", "distance_to_match"
        ],
        errors="ignore"
    )

    # ✅ Rename "Regional Unit English" to "Regional Unit" for display
    df_display = df_display.rename(columns={"Regional Unit English": "Regional Unit"})

    # ✅ Display the DataFrame
    st.dataframe(df_display, use_container_width=True)

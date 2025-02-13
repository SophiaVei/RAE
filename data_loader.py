import pandas as pd

def load_data():
    """Load and preprocess the renewable energy permits dataset."""
    file_path = r"data/permits/final_permits_cleaned.xlsx"
    df = pd.read_excel(file_path, dtype=str)

    # Convert date columns to datetime
    date_cols = ["Application Submission Date", "Permit Issuance Date", "Permit Expiration Date"]
    for col in date_cols:
        df[col] = pd.to_datetime(df[col], errors="coerce")

    # Convert numeric columns
    df["Installed Capacity (MW)"] = pd.to_numeric(df["Installed Capacity (MW)"], errors="coerce")

    return df

def load_fire_data():
    """Load and preprocess the Greece fire dataset."""
    file_path = r"data/other/greece_fires.csv"
    df_fire = pd.read_csv(file_path)

    # Ensure correct data types
    df_fire["Year"] = df_fire["Year"].astype(int)
    df_fire["Burned Area (ha)"] = pd.to_numeric(df_fire["Burned Area (ha)"], errors="coerce")
    df_fire["Number of Fires"] = pd.to_numeric(df_fire["Number of Fires"], errors="coerce")

    # ✅ Remove the last row
    df_fire = df_fire.iloc[:-1]

    return df_fire


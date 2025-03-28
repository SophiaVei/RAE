import pandas as pd

def load_data():
    """Load and preprocess the renewable energy permits dataset."""
    file_path = r"data/permits/final_permits_cleaned.xlsx"

    df = pd.read_excel(file_path, dtype=str)
    # ✅ Drop original Greek "Regional Unit" to avoid column conflict
    if "Regional Unit" in df.columns and "Regional Unit English" in df.columns:
        df.drop(columns=["Regional Unit"], inplace=True)

    # ✅ Rename English version to standard column name
    df.rename(columns={"Regional Unit English": "Regional Unit"}, inplace=True)

    # Convert date columns to datetime
    date_cols = ["Application Submission Date", "Permit Issuance Date", "Permit Expiration Date"]
    for col in date_cols:
        df[col] = pd.to_datetime(df[col], errors="coerce")

    # Convert numeric columns
    df["Installed Capacity (MW)"] = pd.to_numeric(df["Installed Capacity (MW)"], errors="coerce")

    return df


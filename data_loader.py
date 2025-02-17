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


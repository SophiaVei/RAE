import pandas as pd


def load_data():
    """Load and preprocess the renewable energy permits dataset."""
    file_path = r"\data\permits\final_permits_cleaned.xlsx"
    df = pd.read_excel(file_path, dtype=str)

    # Convert date columns to datetime
    date_cols = ["ΗΜΕΡΟΜΗΝΙΑ ΥΠΟΒΟΛΗΣ ΑΙΤΗΣΗΣ", "ΗΜΕΡΟΜΗΝΙΑ ΕΚΔ. ΑΔ.ΠΑΡΑΓΩΓΗΣ", "ΗΜΕΡΟΜΗΝΙΑ ΛΗΞΗΣ ΑΔ.ΠΑΡΑΓΩΓΗΣ"]
    for col in date_cols:
        df[col] = pd.to_datetime(df[col], errors="coerce")

    # Convert numeric columns
    df["ΜΕΓΙΣΤΗ ΙΣΧΥΣ (MW)"] = pd.to_numeric(df["ΜΕΓΙΣΤΗ ΙΣΧΥΣ (MW)"], errors="coerce")

    return df

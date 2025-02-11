import pandas as pd
import os
import numpy as np
import unicodedata
from thefuzz import process

# Define base directory
base_dir = r"data\permits"

# List of Excel files to process
excel_files = [
    "2020-12 - Dec.xlsx", "2021-03 - Mar.xlsx", "2021-05 - May.xlsx", "2021-08 - Aug.xlsx",
    "2021-10 - Oct.xlsx", "2022-03 - Mar.xlsx", "2022-09 - Sep.xlsx", "2022-12 - Dec.xlsx",
    "2023-01 - Jan.xlsx", "2023-02 - Feb.xlsx", "2023-03 - Mar.xlsx", "2023-05 - May.xlsx",
    "2023-06 - Jun.xlsx", "2023-07 - Jul.xlsx", "2023-09 - Sep.xlsx", "2023-10 - Oct.xlsx",
    "2023-11 - Nov.xlsx", "2024-02 - Feb.xlsx", "2024-03 - Mar.xlsx", "2024-05 - May.xlsx",
    "2024-09 - Sep.xlsx", "2024-10 - Oct.xlsx", "2024-11 - Nov.xlsx", "2024-12 - Dec.xlsx"
]

required_columns = [
    "ΑΡΙΘΜΟΣ ΜΗΤΡΩΟΥ ΑΔΕΙΩΝ", "ΗΜΕΡΟΜΗΝΙΑ ΥΠΟΒΟΛΗΣ ΑΙΤΗΣΗΣ", "ΗΜΕΡΟΜΗΝΙΑ ΕΚΔ. ΑΔ.ΠΑΡΑΓΩΓΗΣ",
    "ΗΜΕΡΟΜΗΝΙΑ ΛΗΞΗΣ ΑΔ.ΠΑΡΑΓΩΓΗΣ", "ΠΕΡΙΦΕΡΕΙΑ", "ΠΕΡΙΦΕΡΕΙΑΚΗ ΕΝΟΤΗΤΑ", "ΔΗΜΟΣ",
    "ΜΕΓΙΣΤΗ ΙΣΧΥΣ (MW)", "ΤΕΧΝΟΛΟΓΙΑ"
]

# Merging all files into a single DataFrame
df_all = pd.DataFrame()

for file_name in excel_files:
    input_path = os.path.join(base_dir, file_name)

    try:
        # Load the Excel file, skipping the first row
        df_temp = pd.read_excel(input_path, dtype=str, skiprows=1)

        # Trim spaces from column names
        df_temp.columns = df_temp.columns.str.strip()

        # Rename incorrect column names if they exist
        column_rename_map = {
            "AΡΙΘΜΟΣ ΜΗΤΡΩΟΥ ΑΔΕΙΩΝ": "ΑΡΙΘΜΟΣ ΜΗΤΡΩΟΥ ΑΔΕΙΩΝ",
            "ΗΜΕΡΟΜΗΝΙΑ ΛΗΞΗΣ ΑΔ. ΠΑΡΑΓΩΓΗΣ": "ΗΜΕΡΟΜΗΝΙΑ ΛΗΞΗΣ ΑΔ.ΠΑΡΑΓΩΓΗΣ"
        }
        df_temp.rename(columns=column_rename_map, inplace=True)

        # Keep only required columns if they exist
        missing_columns = [col for col in required_columns if col not in df_temp.columns]
        if missing_columns:
            print(f"Skipping {file_name}: Missing columns {missing_columns}")
            continue

        df_temp = df_temp[required_columns]
        df_all = pd.concat([df_all, df_temp])

    except Exception as e:
        print(f"Error processing {file_name}: {e}")

# Reset index after merging
df_all = df_all.reset_index(drop=True)

# Convert date columns to datetime (AFTER merging)
date_columns = ["ΗΜΕΡΟΜΗΝΙΑ ΥΠΟΒΟΛΗΣ ΑΙΤΗΣΗΣ", "ΗΜΕΡΟΜΗΝΙΑ ΕΚΔ. ΑΔ.ΠΑΡΑΓΩΓΗΣ", "ΗΜΕΡΟΜΗΝΙΑ ΛΗΞΗΣ ΑΔ.ΠΑΡΑΓΩΓΗΣ"]
for col in date_columns:
    df_all[col] = pd.to_datetime(df_all[col], errors="coerce", dayfirst=True)

# Fix incorrect expiration years (e.g., 1935 -> 2035, 1945 -> 2045, 1946 -> 2046)
df_all["ΗΜΕΡΟΜΗΝΙΑ ΛΗΞΗΣ ΑΔ.ΠΑΡΑΓΩΓΗΣ"] = df_all["ΗΜΕΡΟΜΗΝΙΑ ΛΗΞΗΣ ΑΔ.ΠΑΡΑΓΩΓΗΣ"].apply(
    lambda x: x.replace(year=x.year + 100) if x.year in [1935, 1945, 1946] else x
)


# Drop rows with invalid dates AFTER merging
df_all = df_all.dropna(subset=date_columns)

# Convert power column to numeric
df_all["ΜΕΓΙΣΤΗ ΙΣΧΥΣ (MW)"] = pd.to_numeric(df_all["ΜΕΓΙΣΤΗ ΙΣΧΥΣ (MW)"], errors="coerce")

# Debug check for non-numeric values
non_numeric_power = df_all[df_all["ΜΕΓΙΣΤΗ ΙΣΧΥΣ (MW)"].isna()]


# Sort by ΑΡΙΘΜΟΣ ΜΗΤΡΩΟΥ ΑΔΕΙΩΝ (ascending) and ΗΜΕΡΟΜΗΝΙΑ ΛΗΞΗΣ ΑΔ.ΠΑΡΑΓΩΓΗΣ (descending)
df_all = df_all.sort_values(by=["ΑΡΙΘΜΟΣ ΜΗΤΡΩΟΥ ΑΔΕΙΩΝ", "ΗΜΕΡΟΜΗΝΙΑ ΛΗΞΗΣ ΑΔ.ΠΑΡΑΓΩΓΗΣ"], ascending=[True, False])

# Remove duplicate permits, keeping the latest expiration date
df_all = df_all.drop_duplicates(subset=["ΑΡΙΘΜΟΣ ΜΗΤΡΩΟΥ ΑΔΕΙΩΝ"], keep="last").reset_index(drop=True)

def clean_text(text):
    """Normalize Greek text to remove diacritics and standardize spacing."""
    if isinstance(text, str):
        text = text.strip()  # Remove leading/trailing spaces
        text = text.replace("ΐ", "ι").replace("ϊ", "ι")  # Normalize diacritics
        text = text.replace("Ϊ", "Ι")  # Handle uppercase variants
        text = text.replace("\u200b", "")  # Remove zero-width spaces
        text = unicodedata.normalize("NFKC", text)  # Normalize Unicode characters
    return text

df_all["ΤΕΧΝΟΛΟΓΙΑ"] = df_all["ΤΕΧΝΟΛΟΓΙΑ"].apply(clean_text)


# Standardize the "ΠΕΡΙΦΕΡΕΙΑ" column by stripping spaces, making uppercase, and mapping values
df_all["ΠΕΡΙΦΕΡΕΙΑ"] = df_all["ΠΕΡΙΦΕΡΕΙΑ"].str.strip().str.upper()

# Replace missing or incorrect values in ΠΕΡΙΦΕΡΕΙΑ
df_all["ΠΕΡΙΦΕΡΕΙΑ"] = df_all["ΠΕΡΙΦΕΡΕΙΑ"].replace({np.nan: "ΑΓΝΩΣΤΗ ΠΕΡΙΦΕΡΕΙΑ"})

# Ensure that no dates accidentally appear in ΠΕΡΙΦΕΡΕΙΑ
df_all["ΠΕΡΙΦΕΡΕΙΑ"] = df_all["ΠΕΡΙΦΕΡΕΙΑ"].astype(str)  # Ensure it's a string column
df_all["ΠΕΡΙΦΕΡΕΙΑ"] = df_all["ΠΕΡΙΦΕΡΕΙΑ"].apply(lambda x: x if not x.startswith("20") else "ΑΓΝΩΣΤΗ ΠΕΡΙΦΕΡΕΙΑ")

# Define mapping for fixing inconsistencies in "ΠΕΡΙΦΕΡΕΙΑ"
perifereia_map = {
    "Κ ΜΑΚΕΔΟΝΙΑΣ": "ΚΕΝΤΡΙΚΗΣ ΜΑΚΕΔΟΝΙΑΣ",
    "ΣΤ ΕΛΛΑΔΑΣ": "ΣΤΕΡΕΑΣ ΕΛΛΑΔΟΣ",
    "ΣΤΕΡΕΑ ΕΛΛΑΔΑ": "ΣΤΕΡΕΑΣ ΕΛΛΑΔΟΣ",
    "ΣΤΕΡΕΑΣ ΕΛΛΑΔΑΣ": "ΣΤΕΡΕΑΣ ΕΛΛΑΔΟΣ",
    "ΣΤΕΡΕΆΣ ΕΛΛΆΔΑΣ": "ΣΤΕΡΕΑΣ ΕΛΛΑΔΟΣ",
    "ΣΤΕΡΑΙΑΣ ΕΛΛΑΔΑΣ": "ΣΤΕΡΕΑΣ ΕΛΛΑΔΟΣ",
    "Ν ΑΙΓΑΙΟΥ": "ΝΟΤΙΟΥ ΑΙΓΑΙΟΥ",
    "ΑΝ. ΜΑΚΕΔΟΝΙΑΣ & ΘΡΑΚΗΣ": "ΑΝΑΤΟΛΙΚΗΣ ΜΑΚΕΔΟΝΙΑΣ ΚΑΙ ΘΡΑΚΗΣ",
    "Δ. ΕΛΛΑΔΑΣ": "ΔΥΤΙΚΗΣ ΕΛΛΑΔΟΣ",
    "ΔΥΤΙΚΉΣ ΕΛΛΆΔΑΣ": "ΔΥΤΙΚΗΣ ΕΛΛΑΔΟΣ",
    "ΔΥΤΙΚΉΣ ΕΛΛΆΔΑΣ": "ΔΥΤΙΚΗΣ ΕΛΛΑΔΟΣ",
    "ΔΥΤΙΚΗΣ ΕΛΛΑΔOΣ": "ΔΥΤΙΚΗΣ ΕΛΛΑΔΟΣ",
    "ΔΥΤΙΚΗΣ ΕΛΛΑΔΑΣ": "ΔΥΤΙΚΗΣ ΕΛΛΑΔΟΣ",
    "Δ ΕΛΛΑΔΑΣ": "ΔΥΤΙΚΗΣ ΕΛΛΑΔΟΣ",
    "Β ΑΙΓΑΙΟΥ": "ΒΟΡΕΙΟΥ ΑΙΓΑΙΟΥ",
    "Δ ΜΑΚΕΔΟΝΙΑΣ": "ΔΥΤΙΚΗΣ ΜΑΚΕΔΟΝΙΑΣ",
    "ΑΝ ΜΑΚΕΔΟΝΙΑΣ ΘΡΑΚΗΣ": "ΑΝΑΤΟΛΙΚΗΣ ΜΑΚΕΔΟΝΙΑΣ ΚΑΙ ΘΡΑΚΗΣ",
    "ΑΝΑΤΟΛΙΚΗ ΜΑΚΕΔΟΝΙΑ ΚΑΙ ΘΡΑΚΗΣ": "ΑΝΑΤΟΛΙΚΗΣ ΜΑΚΕΔΟΝΙΑΣ ΚΑΙ ΘΡΑΚΗΣ",
    "ΑΝ.ΜΑΚΕΔΟΝΙΑΣ ΚΑΙ ΘΡΑΚΗΣ": "ΑΝΑΤΟΛΙΚΗΣ ΜΑΚΕΔΟΝΙΑΣ ΚΑΙ ΘΡΑΚΗΣ",
    "ΑΝΑΤΟΛΙΚΗΣ ΜΑΚΕΔΟΝΙΑΣ & ΘΡΑΚΗΣ": "ΑΝΑΤΟΛΙΚΗΣ ΜΑΚΕΔΟΝΙΑΣ ΚΑΙ ΘΡΑΚΗΣ",
    "ΑΝΑΤΟΛΙΚΗΣ ΜΑΚΕΔΟΝΙΑΣ ΘΡΑΚΗΣ": "ΑΝΑΤΟΛΙΚΗΣ ΜΑΚΕΔΟΝΙΑΣ ΚΑΙ ΘΡΑΚΗΣ",
    "ΙΟΝΙΩΝ ΝΗΣΩΝ": "ΙΟΝΙΩΝ ΝΗΣΙΩΝ",
    "ΘΕΣΣΑΛΙΑΣ,ΗΠΕΙΡΟΥ": "ΘΕΣΣΑΛΙΑΣ, ΗΠΕΙΡΟΥ",
    "ΘΕΣΣΑΛΙΑΣ,ΗΠΕΙΡΟΥ": "ΘΕΣΣΑΛΙΑΣ, ΗΠΕΙΡΟΥ",
    "ΗΠΕΙΡΟΥ & ΘΕΣΣΑΛΙΑΣ": "ΘΕΣΣΑΛΙΑΣ, ΗΠΕΙΡΟΥ",
    "ΗΠΕΙΡΟΥ - ΘΕΣΣΑΛΙΑΣ": "ΘΕΣΣΑΛΙΑΣ, ΗΠΕΙΡΟΥ",
    "ΔΥΤΙΚΉΣ ΕΛΛΆΔΑΣ, ΣΤΕΡΕΆΣ ΕΛΛΆΔΑΣ": "ΔΥΤΙΚΗΣ ΕΛΛΑΔOΣ, ΣΤΕΡΕΑΣ ΕΛΛΑΔOΣ",
    "ΣΤΕΡΑΙΑΣ ΕΛΛΑΔΑΣ & ΔΥΤΙΚΗΣ ΕΛΛΑΔΑΣ": "ΔΥΤΙΚΗΣ ΕΛΛΑΔOΣ, ΣΤΕΡΕΑΣ ΕΛΛΑΔOΣ",
    "ΔΥΤΙΚΗΣ ΕΛΛΑΔΟΣ & ΣΤΕΡΕΑΣ ΕΛΛΑΔΟΣ": "ΔΥΤΙΚΗΣ ΕΛΛΑΔOΣ, ΣΤΕΡΕΑΣ ΕΛΛΑΔOΣ",
    "ΔΥΤΙΚΗΣ ΕΛΛΑΔΑΣ, ΣΤΕΡΕΑΣ ΕΛΛΑΔΑΣ": "ΔΥΤΙΚΗΣ ΕΛΛΑΔOΣ, ΣΤΕΡΕΑΣ ΕΛΛΑΔOΣ",
    "Δ. ΜΑΚΕΔΟΝΙΑΣ - Κ. ΜΑΚΕΔΟΝΙΑΣ": "ΔΥΤΙΚΗΣ ΜΑΚΕΔΟΝΙΑΣ, ΚΕΝΤΡΙΚΗΣ ΜΑΚΕΔΟΝΙΑΣ",
    "ΔΥΤΙΚΗΣ ΜΑΚΕΔΟΝΙΑΣ,ΚΕΝΤΡΙΚΗΣ ΜΑΚΕΔΟΝΙΑΣ": "ΔΥΤΙΚΗΣ ΜΑΚΕΔΟΝΙΑΣ, ΚΕΝΤΡΙΚΗΣ ΜΑΚΕΔΟΝΙΑΣ",
    "ΣΤΕΡΕΑΣ ΕΛΛΑΔΑΣ - ΘΕΣΣΑΛΙΑΣ": "ΣΤΕΡΕΑΣ ΕΛΛΑΔΟΣ, ΘΕΣΣΑΛΙΑΣ",
    "ΘΕΣΣΑΛΙΑΣ,ΣΤΕΡΕΑΣ ΕΛΛΑΔΑΣ": "ΣΤΕΡΕΑΣ ΕΛΛΑΔΟΣ, ΘΕΣΣΑΛΙΑΣ",
    "ΣΤΕΡΕΑΣ ΕΛΛΑΔΟΣ - ΘΕΣΣΑΛΙΑΣ": "ΣΤΕΡΕΑΣ ΕΛΛΑΔΟΣ, ΘΕΣΣΑΛΙΑΣ",
    "ΑΝ. ΜΑΚΕΔΟΝΙΑΣ & ΘΡΑΚΗΣ,ΚΕΝΤΡΙΚΗΣ ΜΑΚΕΔΟΝΙΑΣ": "ΑΝΑΤΟΛΙΚΗΣ ΜΑΚΕΔΟΝΙΑΣ ΚΑΙ ΘΡΑΚΗΣ, ΚΕΝΤΡΙΚΗΣ ΜΑΚΕΔΟΝΙΑΣ",
    "ΔΥΤΙΚΗΣ ΜΑΚΕΔΟΝΙΑΣ,ΘΕΣΣΑΛΙΑΣ": "ΔΥΤΙΚΗΣ ΜΑΚΕΔΟΝΙΑΣ, ΘΕΣΣΑΛΙΑΣ",
    "ΘΕΣΣΑΛΙΑΣ,ΔΥΤΙΚΗΣ ΜΑΚΕΔΟΝΙΑΣ": "ΔΥΤΙΚΗΣ ΜΑΚΕΔΟΝΙΑΣ, ΘΕΣΣΑΛΙΑΣ",
    "ΚΕΝΤΡΙΚΗΣ ΜΑΚΕΔΟΝΙΑΣ - ΘΕΣΣΑΛΙΑΣ": "ΚΕΝΤΡΙΚΗΣ ΜΑΚΕΔΟΝΙΑΣ, ΘΕΣΣΑΛΙΑΣ",
    "ΠΕΛΟΠΟΝΝΗΣΟΥ - ΔΥΤΙΚΗΣ ΕΛΛΑΔΑΣ": "ΠΕΛΟΠΟΝΝΗΣΟΥ, ΔΥΤΙΚΗΣ ΕΛΛΑΔOΣ",
    "ΠΕΛΟΠΟΝΝΗΣΟΥ - ΑΤΤΙΚΗΣ": "ΠΕΛΟΠΟΝΝΗΣΟΥ, ΑΤΤΙΚΗΣ",
    "ΘΕΣΣΑΛΙΑΣ - ΗΠΕΙΡΟΥ": "ΘΕΣΣΑΛΙΑΣ, ΗΠΕΙΡΟΥ",
    "ΑΤΤΙΚΗΣ,ΣΤΕΡΕΑΣ ΕΛΛΑΔΑΣ": "ΑΤΤΙΚΗΣ, ΣΤΕΡΕΑΣ ΕΛΛΑΔOΣ",


}
df_all["ΤΕΧΝΟΛΟΓΙΑ"] = df_all["ΤΕΧΝΟΛΟΓΙΑ"].str.strip().str.replace(r'\s*-\s*', '-', regex=True)

df_all["ΠΕΡΙΦΕΡΕΙΑ"] = df_all["ΠΕΡΙΦΕΡΕΙΑ"].replace(perifereia_map)

# Mapping of ΠΕΡΙΦΕΡΕΙΑ to latitude and longitude
perifereia_coordinates = {
    "ΑΤΤΙΚΗΣ": (37.9838, 23.7275),
    "ΚΕΝΤΡΙΚΗΣ ΜΑΚΕΔΟΝΙΑΣ": (40.6401, 22.9444),
    "ΔΥΤΙΚΗΣ ΕΛΛΑΔΟΣ": (38.2466, 21.7346),
    "ΣΤΕΡΕΑΣ ΕΛΛΑΔΟΣ": (38.8951, 22.4341),
    "ΘΕΣΣΑΛΙΑΣ": (39.6390, 22.4191),
    "ΠΕΛΟΠΟΝΝΗΣΟΥ": (37.0000, 22.0000),
    "ΒΟΡΕΙΟΥ ΑΙΓΑΙΟΥ": (39.1126, 26.5540),
    "ΝΟΤΙΟΥ ΑΙΓΑΙΟΥ": (36.3932, 25.4615),
    "ΗΠΕΙΡΟΥ": (39.6650, 20.8537),
    "ΑΝΑΤΟΛΙΚΗΣ ΜΑΚΕΔΟΝΙΑΣ ΚΑΙ ΘΡΑΚΗΣ": (41.1230, 24.8820),
    "ΔΥΤΙΚΗΣ ΜΑΚΕΔΟΝΙΑΣ": (40.3000, 21.7889),
    "ΙΟΝΙΩΝ ΝΗΣΙΩΝ": (38.3087, 20.7072),
}

# Add latitude and longitude columns based on ΠΕΡΙΦΕΡΕΙΑ
df_all["LAT"] = df_all["ΠΕΡΙΦΕΡΕΙΑ"].map(lambda x: perifereia_coordinates.get(x, np.nan)[0] if x in perifereia_coordinates else np.nan)
df_all["LON"] = df_all["ΠΕΡΙΦΕΡΕΙΑ"].map(lambda x: perifereia_coordinates.get(x, np.nan)[1] if x in perifereia_coordinates else np.nan)

# Debugging check
missing_coords = df_all[df_all["LAT"].isna()]
if not missing_coords.empty:
    print("⚠️ Missing coordinates for the following regions:", missing_coords["ΠΕΡΙΦΕΡΕΙΑ"].unique())


# Save the cleaned dataset
final_output_file = os.path.join(base_dir, "final_permits_cleaned.xlsx")
df_all.to_excel(final_output_file, index=False)

print(f"Final number of unique permits: {len(df_all.index)}")
print(f"Cleaned dataset saved to: {final_output_file}")

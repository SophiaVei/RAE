
---

## 1. Data Acquisition

1. **Source**  
   All raw permit‐application spreadsheets were downloaded manually from the Greek Regulatory Authority for Energy (RAE) portal, one file per quarter or month (e.g. `2020‑12 – Dec.xlsx`, …, `2024‑12 – Dec.xlsx`).

2. **Location**  
   Place every `.xlsx` into `data/permits/` before running preprocessing.

---

## 2. Preprocessing 
- **Merging**  
  Concatenate 24 monthly/quarterly workbooks into one DataFrame.

- **Filtering**  
  Skip any sheet missing a required column.

- **Renaming**  
  Fix header typos (`AΡΙΘΜΟΣ…`, `ΗΜΕΡΟΜΗΝΙΑ ΛΗΞΗΣ…`).

- **Date formatting**  
  - Parse three Greek‑named date columns → `datetime`  
  - Correct century errors (+100 years for known bad values).

- **Dropping invalid**  
  Remove rows where any date parse failed.

- **Conversion**  
  Cast `"ΜΕΓΙΣΤΗ ΙΣΧΥΣ (MW)"` → numeric.

- **Sorting & deduplication**  
  Sort by permit ID ascending, expiration descending → keep latest record.

- **Text normalization**  
  - Strip & Unicode‑normalize Greek text  
  - Remove diacritics, zero‑width spaces & stray hyphens.

- **Standardization**  
  Uppercase/strip & map dozens of Region/Prefecture variants → canonical names.

- **Aggregation**  
  Collapse “combined‑region” rows (`,` → `"ΑΛΛΕΣ"`).

- **Geocoding**  
  Hard‑coded centroid lookup for regions & prefectures.

- **Spatial join**  
  Nearest‑neighbor join of permit‑point → prefecture polygon.

- **Column translations**  
  Rename Greek column headers → English (`Company`, `Region`, `Technology`, etc.).

- **Export**  
  Save final Excel (`final_permits_cleaned.xlsx`) for downstream API & visualization.











# Build and Run the Docker Containers
docker-compose up --build

# View Swagger API Docs
http://localhost:5001/apidocs/

## API Endpoints & Visualization Mapping Guide: [Guide](https://docs.google.com/document/d/14T9Wm9U5U6pzQF5xWnoTQaE6KA2rXfQPnBXXn5BJbd0/edit?tab=t.0)

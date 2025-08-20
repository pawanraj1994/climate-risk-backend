# rainfall_module.py

import pandas as pd
import numpy as np
import os

# Relative path (works locally + on Render)
DATA_FILE = os.path.join("data", "preprocessed_composite_matrix.csv")

try:
    df = pd.read_csv(DATA_FILE)
except FileNotFoundError:
    raise FileNotFoundError(
        f"⚠️ Could not find {DATA_FILE}. "
        "Make sure preprocessed_composite_matrix.csv is inside backend/data/"
    )

def extract_rainfall_indicators(lat, lon):
    """
    Lookup hazard indicators from the preprocessed composite matrix.
    """

    # Round to nearest 0.5°
    lat = round(lat * 2) / 2
    lon = round(lon * 2) / 2

    if lon < 0:  # wrap-around for negatives
        lon += 360

    row = df[(np.isclose(df["LAT"], lat)) & (np.isclose(df["LON"], lon))]

    if row.empty:
        raise ValueError(f"No preprocessed data found for lat={lat}, lon={lon}")

    row = row.iloc[0]

    return {
        "LAT": row["LAT"],
        "LON": row["LON"],
        "ER100": row["ER100"],
        "ER150": row["ER150"],
        "ER_Prob": row["ER_Prob"],
        "RP10": row["RP10"],
        "RP20": row["RP20"],
        "RP50": row["RP50"],
        "RP100": row["RP100"],
        "RP_Avg": row["RP_Avg"],
        "RP_Prob": row["RP_Prob"],
        "P_D1": row["P_D1"],
        "P_D2": row["P_D2"],
        "P_D3": row["P_D3"],
        "P_D4": row["P_D4"],
        "Drought_Prob": row["Drought_Prob"],
        "Composite_Hazard": row["Composite_Hazard"],
    }

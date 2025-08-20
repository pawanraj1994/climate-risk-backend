import xarray as xr
import numpy as np
import pandas as pd
import glob
import os

# Path to NetCDF files
DATA_DIR = r"C:\Users\Pawan\Desktop\climate_risk_app\data"
FILES = sorted(glob.glob(os.path.join(DATA_DIR, "RF25_ind*.nc")))

START_YEAR = 1910
END_YEAR = 2023

def compute_return_periods(annual_max, return_periods=[10,20,50,100]):
    """Weibull plotting position method"""
    n = len(annual_max)
    sorted_max = np.sort(annual_max)[::-1]  # descending
    rp_values = {}
    for rp in return_periods:
        m = int((n + 1) / rp)
        m = max(1, min(m, n))
        rp_values[f"RP{rp}"] = sorted_max[m-1]
    return rp_values

def process_grid():
    results = []

    # Open one sample file to get grid shape
    sample = xr.open_dataset(FILES[0])
    lats = sample["LATITUDE"].values
    lons = sample["LONGITUDE"].values
    sample.close()

    # Loop through all grid cells
    for i, lat in enumerate(lats):
        for j, lon in enumerate(lons):
            daily_series = []

            # Collect daily rainfall across years
            for f in FILES:
                try:
                    ds = xr.open_dataset(f)
                    rain = ds["RAINFALL"].isel(LATITUDE=i, LONGITUDE=j).values
                    if rain is not None and len(rain) > 0:
                        daily_series.extend(rain.tolist())
                    ds.close()
                except Exception as e:
                    print(f"⚠️ Failed {f} at {lat},{lon}: {e}")

            if len(daily_series) < 365*30:  # Require at least 30 years of data
                continue

            daily_series = np.array(daily_series)
            total_days = len(daily_series)

            # --- Extreme Rainfall Probabilities ---
            er100 = np.sum(daily_series > 100) / total_days
            er150 = np.sum(daily_series > 150) / total_days
            er_prob = (er100 + er150) / 2.0

            # --- Yearly grouping ---
            n_years = (END_YEAR - START_YEAR + 1)
            days_per_year = total_days // n_years
            yearly_blocks = [
                daily_series[k*days_per_year:(k+1)*days_per_year]
                for k in range(n_years)
            ]

            # Annual maxima
            annual_max = [np.max(y) for y in yearly_blocks if len(y) > 0]
            rp_vals = compute_return_periods(annual_max, [10,20,50,100])

            # --- RP Hazard Indicator ---
            rp_avg = np.mean(list(rp_vals.values()))

            # --- Drought thresholds ---
            yearly_total = [np.sum(y) for y in yearly_blocks if len(y) > 0]
            mean = np.mean(yearly_total)
            std = np.std(yearly_total)

            p_d1 = sum(y < mean - 1*std for y in yearly_total) / len(yearly_total)
            p_d2 = sum(y < mean - 1.5*std for y in yearly_total) / len(yearly_total)
            p_d3 = sum(y < mean - 2*std for y in yearly_total) / len(yearly_total)
            p_d4 = sum(y < mean - 2.5*std for y in yearly_total) / len(yearly_total)
            drought_prob = (p_d1 + p_d2 + p_d3 + p_d4) / 4.0

            results.append({
                "LAT": round(float(lat),3),
                "LON": round(float(lon),3),
                "ER100": round(er100,4),
                "ER150": round(er150,4),
                "ER_Prob": round(er_prob,4),
                "RP10": round(rp_vals["RP10"],2),
                "RP20": round(rp_vals["RP20"],2),
                "RP50": round(rp_vals["RP50"],2),
                "RP100": round(rp_vals["RP100"],2),
                "RP_Avg": round(rp_avg,2),
                "P_D1": round(p_d1,4),
                "P_D2": round(p_d2,4),
                "P_D3": round(p_d3,4),
                "P_D4": round(p_d4,4),
                "Drought_Prob": round(drought_prob,4),
            })

            print(f"✅ Processed grid {lat},{lon}")

    return pd.DataFrame(results)

if __name__ == "__main__":
    df = process_grid()

    # --- Normalize RP_Avg to 0–1 (RP_Prob) ---
    min_val = df["RP_Avg"].min()
    max_val = df["RP_Avg"].max()
    df["RP_Prob"] = (df["RP_Avg"] - min_val) / (max_val - min_val)

    # --- Composite Hazard Score ---
    df["Composite_Hazard"] = (
        0.4 * df["Drought_Prob"] +
        0.3 * df["ER_Prob"] +
        0.3 * df["RP_Prob"]
    ).round(4)

    out_file = os.path.join(DATA_DIR, "preprocessed_composite_matrix.csv")
    df.to_csv(out_file, index=False)
    print(f"\n📊 Composite Hazard Matrix saved → {out_file}")

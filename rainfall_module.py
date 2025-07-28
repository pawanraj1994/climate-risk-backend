import numpy as np
import xarray as xr

def extract_rainfall_indicators(lat, lon):
    base_url = "https://storage.googleapis.com/rainfall-risk-data"
    years = list(range(1910, 2024))
    rainfall_values = []

    for year in years:
        url = f"{base_url}/RF25_ind{year}_rfp25.nc"
        try:
            ds = xr.open_dataset(url, engine="h5netcdf")
            rain = ds["RAINFALL"].sel(LATITUDE=lat, LONGITUDE=lon, method="nearest").values
            rainfall_values.extend(rain)
            ds.close()
        except Exception as e:
            print(f"⚠️ Failed for year {year}: {e}")
            continue

    rainfall = np.array(rainfall_values)
    if len(rainfall) == 0:
        raise ValueError("No valid rainfall data found.")

    er100_days = np.sum(rainfall > 100)
    er150_days = np.sum(rainfall > 150)
    total_days = len(rainfall)
    p_er100 = round(er100_days / total_days, 3)
    p_er150 = round(er150_days / total_days, 3)

    rainfall_by_year = np.array_split(rainfall, len(years))
    yearly_max = [np.max(y) for y in rainfall_by_year if len(y) > 0]
    rp100 = round(np.percentile(yearly_max, 100 * (1 - 1/100)), 2)

    yearly_total = [np.sum(y) for y in rainfall_by_year if len(y) > 0]
    mean = np.mean(yearly_total)
    std = np.std(yearly_total)
    d1 = round(sum(y < mean - std for y in yearly_total) / len(yearly_total), 3)
    d2 = round(sum(y < mean - 1.5*std for y in yearly_total) / len(yearly_total), 3)
    d3 = round(sum(y < mean - 2*std for y in yearly_total) / len(yearly_total), 3)
    d4 = round(sum(y < mean - 2.5*std for y in yearly_total) / len(yearly_total), 3)

    return {
        "ER100": p_er100,
        "ER150": p_er150,
        "RP100": rp100,
        "P_D1": d1,
        "P_D2": d2,
        "P_D3": d3,
        "P_D4": d4
    }

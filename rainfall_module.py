import numpy as np
import xarray as xr
import gc

def extract_rainfall_indicators(lat, lon):
    base_url = "https://storage.googleapis.com/rainfall-risk-data"
    years = list(range(1910, 2024))
    rainfall_values = []

    successful_years = 0
    failed_years = []

    if lon < 0:
        lon += 360

    print(f"\n🌍 Processing coordinates: lat={lat}, lon={lon}")
    print(f"📁 Base URL: {base_url}")

    for year in years:
        url = f"{base_url}/RF25_ind{year}_rfp25.nc"
        try:
            print(f"📡 Year {year} → {url}")
            ds = xr.open_dataset(url, engine="netcdf4")

            lat_bounds = (float(ds.LATITUDE.min()), float(ds.LATITUDE.max()))
            lon_bounds = (float(ds.LONGITUDE.min()), float(ds.LONGITUDE.max()))

            if not (lat_bounds[0] <= lat <= lat_bounds[1]):
                raise ValueError(f"Latitude {lat} out of range: {lat_bounds}")
            if not (lon_bounds[0] <= lon <= lon_bounds[1]):
                raise ValueError(f"Longitude {lon} out of range: {lon_bounds}")

            rain = ds["RAINFALL"].sel(
                LATITUDE=lat,
                LONGITUDE=lon,
                method="nearest"
            ).values

            if rain is not None and len(rain) > 0:
                rainfall_values.extend(rain.tolist())
                successful_years += 1
                print(f"✅ Year {year}: {len(rain)} values")
            else:
                print(f"⚠️ Year {year}: no data")

            ds.close()
            if year % 10 == 0:
                gc.collect()

        except Exception as e:
            print(f"❌ Year {year} failed: {e}")
            failed_years.append(year)

    print(f"\n📊 Summary: {successful_years} years successful, {len(failed_years)} failed")

    if not rainfall_values:
        raise ValueError(f"No valid rainfall data found. Failed years: {failed_years[:10]}...")

    if successful_years < 10:
        raise ValueError(f"Insufficient data: only {successful_years} years loaded")

    rainfall = np.array(rainfall_values)
    total_days = len(rainfall)

    er100_days = np.sum(rainfall > 100)
    er150_days = np.sum(rainfall > 150)
    p_er100 = round(er100_days / total_days, 3)
    p_er150 = round(er150_days / total_days, 3)

    days_per_year = total_days // successful_years
    rainfall_by_year = [
        rainfall[i * days_per_year:(i + 1) * days_per_year]
        for i in range(successful_years)
    ]

    yearly_max = [np.max(y) for y in rainfall_by_year if len(y) > 0]
    rp100 = round(np.percentile(yearly_max, 100 * (1 - 1 / 100)), 2)

    yearly_total = [np.sum(y) for y in rainfall_by_year if len(y) > 0]
    mean = np.mean(yearly_total)
    std = np.std(yearly_total)

    d1 = round(sum(y < mean - std for y in yearly_total) / len(yearly_total), 3)
    d2 = round(sum(y < mean - 1.5 * std for y in yearly_total) / len(yearly_total), 3)
    d3 = round(sum(y < mean - 2 * std for y in yearly_total) / len(yearly_total), 3)
    d4 = round(sum(y < mean - 2.5 * std for y in yearly_total) / len(yearly_total), 3)

    return {
        "ER100": p_er100,
        "ER150": p_er150,
        "RP100": rp100,
        "P_D1": d1,
        "P_D2": d2,
        "P_D3": d3,
        "P_D4": d4
    }

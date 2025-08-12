import os
import requests 
import pandas as pd
from datetime import datetime, timedelta
import yaml
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Load config
with open("config/config.yaml", "r") as f:
    config = yaml.safe_load(f)

# API keys from environment variables
noaa_token = os.getenv("NOAA_API_TOKEN")
eia_token = os.getenv("EIA_API_KEY")

# Directories
output_dir = Path("data/raw")
output_dir.mkdir(parents=True, exist_ok=True)

def fetch_noaa_weather(city, station_id, days_back=90):
    print(f"\n🌤️ Fetching NOAA weather for {city} | station: {station_id}")
    base_url = "https://www.ncei.noaa.gov/cdo-web/api/v2/data"
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days_back)

    params = {
        "datasetid": "GHCND",                        # ✅ Correct key
        "stationid": station_id,                     # ✅ Correct key
        "startdate": start_date.isoformat(),
        "enddate": end_date.isoformat(),
        "datatypeid": "TMAX,TMIN",                   # ✅ Correct key
        "limit": 1000,
        "units": "metric"
    }

    headers = {"token": noaa_token}

    try:
        response = requests.get(base_url, headers=headers, params=params)
        response.raise_for_status()

        data = response.json().get("results", [])    # ✅ Get only the results list
        print(f"📦 NOAA Response Sample: {data[:2]}")

        if not data:
            print(f"⚠️ No weather data returned for {city} — check station, date, or datatype.")
            return

        # Process data into one row per date
        daily_data = {}
        for item in data:
            date = item["date"][:10]
            if date not in daily_data:
                daily_data[date] = {"tmax": None, "tmin": None}
            if item["datatype"] == "TMAX":
                daily_data[date]["tmax"] = item["value"]
            elif item["datatype"] == "TMIN":
                daily_data[date]["tmin"] = item["value"]

        records = []
        for date, temps in daily_data.items():
            tmax_c = temps["tmax"] / 10.0 if temps["tmax"] is not None else None
            tmin_c = temps["tmin"] / 10.0 if temps["tmin"] is not None else None
            tmax_f = round(tmax_c * 9 / 5 + 32, 2) if tmax_c is not None else None
            tmin_f = round(tmin_c * 9 / 5 + 32, 2) if tmin_c is not None else None
            avg_temp_f = round((tmax_f + tmin_f) / 2, 2) if tmax_f and tmin_f else None

            records.append({
                "datetime": date,
                "city": city,
                "tmax_f": tmax_f,
                "tmin_f": tmin_f,
                "avg_temp_f": avg_temp_f
            })

        df = pd.DataFrame(records)
        df["datetime"] = pd.to_datetime(df["datetime"])
        df.sort_values("datetime", inplace=True)

        output_file = output_dir / f"{city}_weather.csv"
        df.to_csv(output_file, index=False)
        print(f"✅ Saved {city} weather data to {output_file}")

    except Exception as e:
        print(f"❌ Failed to fetch NOAA data for {city}: {e}")





def fetch_eia_energy(city, region, days_back=90):
    print(f"\n⚡ Fetching EIA energy for {city} | region: {region}")
    series_id = f"EBA.{region}-ALL.D.H"
    url = f"https://api.eia.gov/v2/seriesid/{series_id}?api_key={eia_token}"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        if "response" not in data or "data" not in data["response"]:
            print(f"❌ No data returned for {city}")
            return

        records = data["response"]["data"]
        df = pd.DataFrame(records)

        if "period" not in df or "value" not in df:
            print(f"❌ Missing expected fields in EIA data for {city}")
            return

        df = df.rename(columns={"period": "datetime", "value": "energy_consumption_mw"})
        df["datetime"] = pd.to_datetime(df["datetime"])
        cutoff = datetime.now() - timedelta(days=days_back)
        df = df[df["datetime"] >= cutoff]

        df.to_csv(output_dir / f"{city}_energy.csv", index=False)
        print(f"✅ Saved {city} energy data to {output_dir / f'{city}_energy.csv'}")
    except Exception as e:
        print(f"❌ Failed to fetch EIA data for {city}: {e}")



# Main function
def main():
    # This main block is for standalone testing of the fetcher.
    # The main pipeline now controls which cities are fetched.
    for city, info in config["cities"].items():
        fetch_noaa_weather(city, info["station_id"])
        fetch_eia_energy(city, info["eia_region"])

if __name__ == "__main__":
    main()

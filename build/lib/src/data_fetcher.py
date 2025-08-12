import os
import yaml
import time
import logging
import requests
import pandas as pd
from datetime import datetime, timedelta

# Setup logging
logging.basicConfig(
    filename='logs/pipeline.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Load config
with open('config/config.yaml', 'r') as file:
    config = yaml.safe_load(file)

API_NOAA = config['api_keys']['noaa_api_token']
API_EIA = config['api_keys']['eia_api_key']
DAYS_BACK = config['settings']['days_back']
CITIES = config['cities']
RAW_DIR = config['paths']['raw_data_dir']

# Date range
END_DATE = datetime.today().date()
START_DATE = END_DATE - timedelta(days=DAYS_BACK)

# NOAA helper
def fetch_noaa_weather(city_dict, start_date, end_date):
    station_id = city_dict['station_id']
    city_name = city_dict['name']

    url = 'https://www.ncei.noaa.gov/cdo-web/api/v2/data'
    headers = {'token': API_NOAA}
    params = {
        'datasetid': 'GHCND',
        'datatypeid': ['TMAX', 'TMIN'],
        'stationid': station_id,
        'startdate': str(start_date),
        'enddate': str(end_date),
        'limit': 1000,
        'units': 'metric'
    }

    for attempt in range(3):
        try:
            response = requests.get(url, headers=headers, params=params)
            if response.status_code == 200:
                records = response.json().get('results', [])
                df = pd.DataFrame(records)
                if df.empty:
                    logging.warning(f"No data returned for {city_name}")
                    return None

                df = df.pivot_table(index='date', columns='datatype', values='value', aggfunc='first').reset_index()
                df['tmax_f'] = df['TMAX'].apply(lambda c: round((c / 10) * 9/5 + 32, 2) if pd.notnull(c) else None)
                df['tmin_f'] = df['TMIN'].apply(lambda c: round((c / 10) * 9/5 + 32, 2) if pd.notnull(c) else None)
                df['city'] = city_name
                df = df[['date', 'city', 'tmax_f', 'tmin_f']]
                return df
            else:
                logging.warning(f"NOAA API call failed for {city_name} on attempt {attempt+1}: {response.status_code}")
                time.sleep(2 ** attempt)
        except Exception as e:
            logging.error(f"Error fetching NOAA weather for {city_name}: {e}")
            time.sleep(2 ** attempt)
    return None

# EIA helper
def fetch_eia_energy(city_dict, start_date, end_date):
    region_code = city_dict['eia_region']
    city_name = city_dict['name']

    url = f"https://api.eia.gov/v2/electricity/rto/region-data/data/"
    params = {
        'api_key': API_EIA,
        'frequency': 'daily',
        'data[]': 'value',
        'facets[respondent][]': region_code,
        'start': str(start_date),
        'end': str(end_date)
    }

    for attempt in range(3):
        try:
            response = requests.get(url, params=params)
            if response.status_code == 200:
                data = response.json().get('response', {}).get('data', [])
                if not data:
                    logging.warning(f"No energy data for {city_name}")
                    return None

                df = pd.DataFrame(data)
                df['date'] = pd.to_datetime(df['period']).dt.date
                df['energy_mwh'] = df['value']
                df['city'] = city_name
                df = df[['date', 'city', 'energy_mwh']]
                return df
            else:
                logging.warning(f"EIA API call failed for {city_name} on attempt {attempt+1}: {response.status_code}")
                time.sleep(2 ** attempt)
        except Exception as e:
            logging.error(f"Error fetching EIA energy for {city_name}: {e}")
            time.sleep(2 ** attempt)
    return None

# Save helper
def save_raw_data(df, path):
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        df.to_csv(path, index=False)
        logging.info(f"Saved data to {path}")
    except Exception as e:
        logging.error(f"Failed to save data to {path}: {e}")

# Main fetching logic for all cities
def run_pipeline():
    for city_key, meta in CITIES.items():
        city_dict = meta.copy()
        city_dict['name'] = city_key

        # Fetch weather
        weather_df = fetch_noaa_weather(city_dict, START_DATE, END_DATE)
        if weather_df is not None:
            weather_path = os.path.join(RAW_DIR, f"weather_{city_key}.csv")
            save_raw_data(weather_df, weather_path)

        # Fetch energy
        energy_df = fetch_eia_energy(city_dict, START_DATE, END_DATE)
        if energy_df is not None:
            energy_path = os.path.join(RAW_DIR, f"energy_{city_key}.csv")
            save_raw_data(energy_df, energy_path)

# Run if script is executed
if __name__ == "__main__":
    run_pipeline()

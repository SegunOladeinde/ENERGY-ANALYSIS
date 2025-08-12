import os
import sys
import logging
import yaml
import pandas as pd
from datetime import datetime
from pathlib import Path
import subprocess
from dotenv import load_dotenv

load_dotenv() # Load .env variables for other modules like data_fetcher

project_root = Path(__file__).resolve().parents[1]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.data_fetcher import fetch_noaa_weather, fetch_eia_energy
from src.data_processor import load_and_merge_city_data, clean_data
from src.data_quality import generate_report as run_data_quality_checks
from src.analysis import analyze_merged_data

# Load config
with open("config/config.yaml", "r") as f:
    config = yaml.safe_load(f)

# Extract config elements
cities = config["cities"]
days_back = config["settings"]["days_back"]
# API keys are now loaded in the modules that use them (e.g., data_fetcher)
# and are no longer needed here.
log_path = config["paths"]["log_file"]
raw_dir = Path(config["paths"]["raw_data_dir"])
processed_dir = Path(config["paths"]["processed_data_dir"])
merged_output_path = processed_dir / "merged_data.csv"

# Setup logging
os.makedirs(os.path.dirname(log_path), exist_ok=True)
logging.basicConfig(
    filename=log_path,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Also log to console
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
console.setFormatter(formatter)
logging.getLogger("").addHandler(console)


def fetch_all_data(cities_config, days):
    """Fetches weather and energy data for all configured cities."""
    logging.info("--- STAGE 1: DATA FETCHING ---")
    for city, info in cities_config.items():
        try:
            logging.info(f"Fetching data for {city}...")
            fetch_noaa_weather(city, info["station_id"], days)
            fetch_eia_energy(city, info["eia_region"], days)
        except Exception as e:
            logging.error(f"Failed to fetch data for {city}: {e}", exc_info=True)
    logging.info("--- Data Fetching Complete ---")


def process_all_data(cities_config):
    """Loads, cleans, and merges data for all cities into a single DataFrame."""
    logging.info("--- STAGE 2: DATA PROCESSING ---")
    all_cleaned_data = []
    for city in cities_config.keys():
        try:
            logging.info(f"Processing data for {city}...")
            merged_df = load_and_merge_city_data(city)
            if merged_df is None:
                logging.warning(f"Skipping {city}: missing or invalid raw data.")
                continue
            cleaned_df = clean_data(merged_df)
            all_cleaned_data.append(cleaned_df)
        except Exception as e:
            logging.error(f"Failed to process data for {city}: {e}", exc_info=True)

    if not all_cleaned_data:
        logging.error("No data was successfully processed.")
        return None

    final_df = pd.concat(all_cleaned_data, ignore_index=True)
    final_df = final_df.sort_values(by=["city", "datetime"])
    logging.info("--- Data Processing Complete ---")
    return final_df


def run_downstream_scripts():
    """Runs downstream scripts like analysis after the main pipeline work."""
    logging.info("--- STAGE 3: RUNNING DOWNSTREAM SCRIPTS ---")
    try:
        logging.info("Running data quality checks...")
        run_data_quality_checks()
        logging.info("Running data analysis...")
        analyze_merged_data()
        logging.info("--- Downstream scripts complete ---")
    except Exception as e:
        logging.error(f"Failed to run downstream scripts: {e}", exc_info=True)


def run_pipeline():
    logging.info("🚀 Pipeline started.")
    
    fetch_all_data(cities, days_back)
    final_df = process_all_data(cities)
    
    if final_df is not None:
        final_df.to_csv(merged_output_path, index=False)
        logging.info(f"✅ Merged data saved to {merged_output_path}")
        run_downstream_scripts()
    else:
        logging.error("Pipeline halted due to processing failure.")

    logging.info("🏁 Pipeline completed.")

if __name__ == "__main__":
    run_pipeline()

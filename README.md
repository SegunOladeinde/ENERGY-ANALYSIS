ENERGY-ANALYSIS 
## Project Overview
This project tackles the costly challenge of inaccurate energy demand forecasting by integrating real-time weather data (NOAA) with energy consumption data (EIA). It delivers a fully automated Python ETL pipeline and an interactive Streamlit dashboard, enabling utilities to make data-driven decisions that optimize power generation, reduce waste, and cut costs — all while showcasing skills in API integration, data engineering, and visualization.


### Key Features

Automated Data Pipeline – Fetches, cleans, and merges weather and energy datasets via API calls.

Configurable Architecture – Uses YAML for environment-specific settings.

Streamlit Dashboard – Interactive visualizations for temperature, demand, and trends.

Data Quality Checks – Validates incoming datasets for missing values and anomalies.

Production-Ready Structure – Modular code for easy scaling and maintenance.


### Tech Stack

.Languages: Python 3

.Libraries: Pandas, Requests, PyYAML, Matplotlib, Streamlit

.APIs: NOAA (weather), EIA (energy)

.Version Control: Git & GitHub

.Deployment: Streamlit 


### Project Structure

project1-energy-analysis/
├── README.md                 # Setup & usage instructions
├── AI_USAGE.md               # AI assistance documentation
├── pyproject.toml            # Dependencies
├── .env.example              # Example API key storage
├── config/
│   └── config.yaml           # Default cities, station IDs, and region codes
├── src/
│   ├── data_fetcher.py       # Fetch NOAA & EIA data
│   ├── data_processor.py     # Cleaning & transformations
│   ├── analysis.py           # Statistical analysis
│   └── pipeline.py           # Orchestrates full workflow
├── dashboards/
│   └── app.py                # Streamlit dashboard
├── logs/
│   └── pipeline.log          # Pipeline logs
├── data/
│   ├── raw/                  # Raw API responses
│   └── processed/            # Clean, ready-to-use data
└── tests/
    └── test_pipeline.py      # Unit tests

## Setup Instructions

1 Clone the Repository
git clone https://github.com/SegunOladeinde/ENERGY-ANALYSIS.git
cd ENERGY-ANALYSIS


2 Create & Activate a Virtual Environment
python -m venv venv
source venv/bin/activate   # Mac/Linux
venv\Scripts\activate      # Windows

3 Install Dependencies
pip install -r requirements.txt


4 Create .env file

Inside the project folder, create a file called .env and add your API keys:

NOAA_API_KEY=your_noaa_api_key_here
EIA_API_KEY=your_eia_api_key_here


Get keys from:

NOAA API token – https://www.ncdc.noaa.gov/cdo-web/token

EIA API key – https://api.eia.gov/v2/electricity/




 ### Default Cities 

The pipeline is configured for:

City	State	NOAA Station ID	EIA Region Code
New York	New York	GHCND:USW00094728	NYIS
Chicago	Illinois	GHCND:USW00094846	PJM
Houston	Texas	GHCND:USW00012960	ERCO
Phoenix	Arizona	GHCND:USW00023183	AZPS
Seattle	Washington	GHCND:USW00024233	SCL

These are stored in config/config.yaml:

cities:
  - name: "New York"
    state: "New York"
    noaa_station: "GHCND:USW00094728"
    eia_region: "NYIS"
  - name: "Chicago"
    state: "Illinois"
    noaa_station: "GHCND:USW00094846"
    eia_region: "PJM"
  - name: "Houston"
    state: "Texas"
    noaa_station: "GHCND:USW00012960"
    eia_region: "ERCO"
  - name: "Phoenix"
    state: "Arizona"
    noaa_station: "GHCND:USW00023183"
    eia_region: "AZPS"
  - name: "Seattle"
    state: "Washington"
    noaa_station: "GHCND:USW00024233"
    eia_region: "SCL"


### Using Different Cities (Optional)

If you want to use different cities instead of the defaults:

Find NOAA Station ID:

Visit NOAA Climate Data Online

Search your city

Copy the Station ID (e.g., GHCND:USW00023174)

Find EIA Region Code:

Visit EIA Region Codes

Find your city’s corresponding region code (e.g., CISO, FPL)

Example:

Update config/config.yaml:

cities:
  - name: "Los Angeles"
    state: "California"
    noaa_station: "GHCND:USW00023174"
    eia_region: "CISO"
  - name: "Miami"
    state: "Florida"
    noaa_station: "GHCND:USW00012839"
    eia_region: "FPL"


Run the pipeline to start collecting data for the new cities:

python src/pipeline.py

 Running the Pipeline

Fetch 90 days of historical data:

python src/data_fetcher.py --historical


Run daily update:

python src/pipeline.py

📊 Launching the Dashboard
streamlit run dashboards/app.py


The dashboard automatically shows whatever cities are in config.yaml.

📋 Data Quality Checks

Each run checks for:

Missing values

Outliers (temp > 130°F or < -50°F, negative energy usage)

Data freshness

Reports saved to:

data_qualityreport.csv
logs/pipeline.log

import pandas as pd
from pathlib import Path
from datetime import datetime 

RAW_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

def load_and_merge_city_data(city_name):
    weather_path = RAW_DIR / f"{city_name}_weather.csv"
    energy_path = RAW_DIR / f"{city_name}_energy.csv"

    if not weather_path.exists() or not energy_path.exists():
        print(f"⚠️ Skipping {city_name}: missing raw files.")
        return None

    try:
        # Load data
        weather = pd.read_csv(weather_path, parse_dates=["datetime"])
        energy = pd.read_csv(energy_path, parse_dates=["datetime"])

        # Merge on datetime
        df = pd.merge(weather, energy, on="datetime", how="inner")
        df["city"] = city_name

        return df

    except Exception as e:
        print(f"❌ Error loading {city_name}: {e}")
        return None

def clean_data(df):
    initial_count = len(df)

    # Drop missing critical values
    df = df.dropna(subset=["avg_temp_f", "energy_consumption_mw"])

    # Filter out invalid temperatures and energy
    df = df[
        (df["avg_temp_f"] >= -50) & 
        (df["avg_temp_f"] <= 130) & 
        (df["energy_consumption_mw"] >= 0)
    ]

    print(f"🧹 Cleaned {initial_count - len(df)} rows (outliers or missing)")
    return df

def main():
    all_cleaned_data = []

    # Get cities based on available weather files
    for weather_file in RAW_DIR.glob("*_weather.csv"):
        city = weather_file.stem.replace("_weather", "")
        print(f"\n⚙️ Processing {city}...")

        merged = load_and_merge_city_data(city)
        if merged is None:
            continue

        cleaned = clean_data(merged)
        all_cleaned_data.append(cleaned)

    if not all_cleaned_data:
        print("❌ No data processed. Check raw files.")
        return

    # Combine all cities into one DataFrame
    final_df = pd.concat(all_cleaned_data, ignore_index=True)
    final_df = final_df.sort_values(by=["city", "datetime"])

    # Save to processed directory
    output_path = PROCESSED_DIR / "clean_combined_data.csv"
    final_df.to_csv(output_path, index=False)
    print(f"\n✅ All cities processed and saved to: {output_path}")

if __name__ == "__main__":
    main()

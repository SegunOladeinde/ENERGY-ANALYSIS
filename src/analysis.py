import pandas as pd
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Paths
merged_file = Path("data/processed/merged_data.csv")
output_file = Path("data/processed/analysis_report.csv")

def analyze_merged_data():
    try:
        if not merged_file.exists():
            logging.error(f"❌ Merged file not found: {merged_file}")
            return

        logging.info(f"📊 Loading merged data from: {merged_file}")
        df = pd.read_csv(merged_file, parse_dates=["datetime"])

        # Drop rows with missing critical data
        df = df.dropna(subset=["avg_temp_f", "energy_consumption_mw"])

        # Compute descriptive stats
        stats = df.groupby("city")[["avg_temp_f", "energy_consumption_mw"]].agg(["mean", "std", "min", "max"])
        stats.columns = ['_'.join(col) for col in stats.columns]

        # Compute correlation between temperature and energy
        correlations = df.groupby("city").apply(
            lambda g: g["avg_temp_f"].corr(g["energy_consumption_mw"])
        ).reset_index(name="temp_energy_corr")

        # Combine results
        report_df = stats.reset_index().merge(correlations, on="city")

        # Save report
        report_df.to_csv(output_file, index=False)
        logging.info(f"✅ Saved analysis report to {output_file}")
        print(report_df)

    except Exception as e:
        logging.error(f"❌ Error during analysis: {e}")

if __name__ == "__main__":
    analyze_merged_data()

import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta

PROCESSED_FILE = Path("data/processed/merged_data.csv")
REPORT_FILE = Path("data/processed/data_quality_report.csv")

# Thresholds
TEMP_MIN = -50
TEMP_MAX = 130
FRESHNESS_THRESHOLD_DAYS = 3


def load_data():
    if not PROCESSED_FILE.exists():
        raise FileNotFoundError(f"{PROCESSED_FILE} not found. Run data_processor.py first.")
    df = pd.read_csv(PROCESSED_FILE, parse_dates=["datetime"])
    return df


def check_missing_values(df):
    return df.isnull().sum()


def check_outliers(df):
    temp_outliers = df[
        (df["avg_temp_f"] < TEMP_MIN) | (df["avg_temp_f"] > TEMP_MAX)
    ]
    energy_outliers = df[df["energy_consumption_mw"] < 0]
    return temp_outliers, energy_outliers


def check_freshness(df):
    latest_date = df["datetime"].max().date()
    today = datetime.now().date()
    freshness_days = (today - latest_date).days
    is_stale = freshness_days > FRESHNESS_THRESHOLD_DAYS
    return latest_date, freshness_days, is_stale


def quality_metrics_over_time(df):
    # Count missing and outliers by date
    df["missing_temp"] = df["avg_temp_f"].isnull()
    df["missing_energy"] = df["energy_consumption_mw"].isnull()
    df["temp_outlier"] = (df["avg_temp_f"] < TEMP_MIN) | (df["avg_temp_f"] > TEMP_MAX)
    df["energy_outlier"] = df["energy_consumption_mw"] < 0

    daily = df.groupby("datetime").agg({
        "missing_temp": "sum",
        "missing_energy": "sum",
        "temp_outlier": "sum",
        "energy_outlier": "sum"
    }).reset_index()

    return daily


def generate_report():
    print("\n📊 Running data quality checks...")

    df = load_data()
    report = {}

    # Missing values
    missing = check_missing_values(df)
    report["missing_values"] = missing.to_dict()

    # Outliers
    temp_outliers, energy_outliers = check_outliers(df)
    report["temp_outliers_count"] = len(temp_outliers)
    report["energy_outliers_count"] = len(energy_outliers)

    # Freshness
    latest_date, freshness_days, is_stale = check_freshness(df)
    report["latest_date"] = str(latest_date)
    report["days_since_latest"] = freshness_days
    report["data_is_stale"] = is_stale

    # Print summary
    print("\n📌 Summary:")
    for key, value in report.items():
        print(f"  {key}: {value}")

    # Save daily quality metrics
    daily_qc = quality_metrics_over_time(df)
    daily_qc.to_csv(REPORT_FILE, index=False)
    print(f"\n✅ Daily quality metrics saved to {REPORT_FILE}")


if __name__ == "__main__":
    generate_report()

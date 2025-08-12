import unittest
import pandas as pd
import os
from src.data_processor import clean_data

class TestPipeline(unittest.TestCase):

    def setUp(self):
        """Load the already merged processed data once."""
        self.file_path = "data/processed/merged_data.csv"
        if os.path.exists(self.file_path):
            self.df = pd.read_csv(self.file_path, parse_dates=["datetime"])
        else:
            self.df = None

    def test_merged_file_exists(self):
        """Check that the processed merged file exists."""
        self.assertTrue(os.path.exists(self.file_path), "Merged file does not exist.")

    def test_merged_file_loads(self):
        """Ensure the merged file can be loaded and is a DataFrame."""
        self.assertIsInstance(self.df, pd.DataFrame, "Loaded object is not a DataFrame.")
        self.assertGreater(len(self.df), 0, "Merged DataFrame is empty.")

    def test_clean_data_output(self):
        """Check that clean_data() returns expected columns."""
        if self.df is not None:
            cleaned = clean_data(self.df.copy())
            expected_columns = {"datetime", "avg_temp_f", "energy_consumption_mw", "city"}
            self.assertTrue(expected_columns.issubset(cleaned.columns),
                            f"Missing expected columns: {expected_columns - set(cleaned.columns)}")
        else:
            self.skipTest("No data loaded to test clean_data.")

if __name__ == '__main__':
    unittest.main()

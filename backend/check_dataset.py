import pandas as pd
import os

# Get the project root directory
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Path to dataset
csv_path = os.path.join(base_dir, "dataset", "spam.csv")

# Read dataset
df = pd.read_csv(csv_path, encoding="latin-1")

# Show first 5 rows
print("First 5 Rows:\n")
print(df.head())

# Show column names
print("\nColumns:")
print(df.columns)

# Dataset information
print("\nDataset Info:")
print(df.info())

# Missing values
print("\nMissing Values:")
print(df.isnull().sum())
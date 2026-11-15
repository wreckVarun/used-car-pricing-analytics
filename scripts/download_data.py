"""Step 1: download the CarDekho used-car dataset from Kaggle.

The file is saved to data/raw/cardekho_dataset.csv. Kaggle lets anyone
download public datasets from this URL, so no API key is needed.
"""
import io
import os
import urllib.request
import zipfile

# Project folder = the folder above this scripts/ folder.
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATASET_URL = "https://www.kaggle.com/api/v1/datasets/download/manishkr1754/cardekho-used-car-data"
CSV_NAME = "cardekho_dataset.csv"
RAW_DIR = os.path.join(ROOT, "data", "raw")


def main():
    os.makedirs(RAW_DIR, exist_ok=True)
    csv_path = os.path.join(RAW_DIR, CSV_NAME)

    # Skip the download if we already have the file.
    if os.path.exists(csv_path):
        print("Raw data already present:", csv_path)
        return

    print("Downloading dataset from Kaggle...")
    with urllib.request.urlopen(DATASET_URL) as response:
        zip_bytes = response.read()

    # Kaggle sends a zip file. Open it in memory and pull out the CSV.
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zip_file:
        zip_file.extract(CSV_NAME, RAW_DIR)

    size_mb = os.path.getsize(csv_path) / 1_000_000
    print(f"Saved {csv_path} ({size_mb:.1f} MB)")


if __name__ == "__main__":
    main()

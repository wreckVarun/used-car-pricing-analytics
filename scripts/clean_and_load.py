"""Step 2: clean the raw CSV and load it into a SQLite database.

SQLite is a small database stored in one file (data/used_cars.db). It stands
in for MySQL here: the SQL in the sql/ folder would run on MySQL with very
few changes.

Every cleaning step is written to outputs/cleaning_log.csv so anyone can see
how many rows were removed and why.
"""
import os
import sqlite3

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_CSV = os.path.join(ROOT, "data", "raw", "cardekho_dataset.csv")
DB_PATH = os.path.join(ROOT, "data", "used_cars.db")
LOG_PATH = os.path.join(ROOT, "outputs", "cleaning_log.csv")

# A car that has done more than this many km is almost certainly a typo
# (one listing says 3,800,000 km on a 5-year-old car).
MAX_KM = 500_000

# Some model names in the source are cut short or spelled two ways.
# Key = (brand, model as written in the file), value = the name we use.
MODEL_FIXES = {
    ("Hyundai", "Grand"): "Grand i10",
    ("BMW", "3"): "3 Series",
    ("BMW", "5"): "5 Series",
    ("BMW", "6"): "6 Series",
    ("BMW", "7"): "7 Series",
    ("Datsun", "redi-GO"): "RediGO",
    ("Mahindra", "KUV"): "KUV100",
    ("Maruti", "Dzire LXI"): "Swift Dzire",
    ("Maruti", "Dzire VXI"): "Swift Dzire",
    ("Maruti", "Dzire ZXI"): "Swift Dzire",
    ("Maruti", "Vitara"): "Vitara Brezza",
}

TEXT_COLUMNS = ["brand", "model", "seller_type", "fuel_type", "transmission_type"]
INT_COLUMNS = ["vehicle_age", "km_driven", "engine", "seats", "selling_price"]
FLOAT_COLUMNS = ["mileage", "max_power"]

log_rows = []


def log_step(step, rows_before, rows_after, reason):
    """Remember one cleaning step and print it."""
    log_rows.append({
        "step": step,
        "rows_before": rows_before,
        "rows_removed": rows_before - rows_after,
        "rows_after": rows_after,
        "reason": reason,
    })
    print(f"{step}: {rows_before} -> {rows_after} rows ({reason})")


def main():
    df = pd.read_csv(RAW_CSV)
    log_step("load raw csv", len(df), len(df), f"{len(df.columns)} columns in the file")

    # 1. The first column has no name. It is just the row number from an
    #    older version of the file, so we drop it.
    df = df.drop(columns=["Unnamed: 0"])

    # 2. Tidy the text columns: remove stray spaces, fix spelling.
    for col in TEXT_COLUMNS:
        df[col] = df[col].astype(str).str.strip()
    df["brand"] = df["brand"].replace({"ISUZU": "Isuzu"})

    renamed = 0
    for (brand, old_name), new_name in MODEL_FIXES.items():
        match = (df["brand"] == brand) & (df["model"] == old_name)
        df.loc[match, "model"] = new_name
        renamed += match.sum()
    # car_name was just brand + model, so rebuild it from the fixed values.
    df["car_name"] = df["brand"] + " " + df["model"]
    log_step("fix model names", len(df), len(df), f"{renamed} rows renamed, e.g. 'Grand' -> 'Grand i10'")

    # 3. Make sure number columns really are numbers.
    #    errors="coerce" turns anything that is not a number into NaN (missing).
    for col in INT_COLUMNS + FLOAT_COLUMNS:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # 4. A car cannot have 0 seats, so treat 0 as missing.
    df.loc[df["seats"] == 0, "seats"] = None

    # 5. Drop rows with any missing value.
    missing = df.isna().sum()
    missing = missing[missing > 0]
    if len(missing) > 0:
        reason = "missing or impossible values: " + ", ".join(f"{col}={n}" for col, n in missing.items())
    else:
        reason = "no missing values found"
    before = len(df)
    df = df.dropna()
    log_step("drop missing values", before, len(df), reason)

    # 6. Drop exact duplicate listings (same car, same price, same everything).
    before = len(df)
    df = df.drop_duplicates()
    log_step("drop duplicates", before, len(df), "identical rows listed more than once")

    # 7. Drop listings with an unrealistic odometer reading.
    before = len(df)
    df = df[df["km_driven"] <= MAX_KM]
    log_step("drop km outliers", before, len(df), f"km_driven above {MAX_KM:,}")

    # Now that there are no missing values, store whole numbers as integers.
    for col in INT_COLUMNS:
        df[col] = df[col].astype(int)

    # Give every listing an id so the pricing-flag query can point at it.
    df = df.reset_index(drop=True)
    df.insert(0, "listing_id", df.index + 1)

    # Write the clean table to SQLite (replacing it if it already exists).
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    df.to_sql("listings", conn, if_exists="replace", index=False)
    conn.close()

    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    pd.DataFrame(log_rows).to_csv(LOG_PATH, index=False)
    print(f"Loaded {len(df)} clean rows into {DB_PATH}")


if __name__ == "__main__":
    main()

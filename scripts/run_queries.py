"""Step 3: run every .sql file in sql/ and save each result to outputs/ as CSV.

The files run in name order (01_, 02_, ...). The CSV gets the same name as
the query, e.g. sql/02_depreciation_by_age.sql -> outputs/02_depreciation_by_age.csv
"""
import glob
import os
import sqlite3
import statistics

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(ROOT, "data", "used_cars.db")
SQL_DIR = os.path.join(ROOT, "sql")
OUTPUT_DIR = os.path.join(ROOT, "outputs")


class Median:
    """SQLite has no MEDIAN() function (MySQL doesn't either), so we add one.

    SQLite calls step() once for every row in a group, then finalize() once
    to get the answer. Empty values (NULL) are skipped, like AVG() does.
    """

    def __init__(self):
        self.values = []

    def step(self, value):
        if value is not None:
            self.values.append(value)

    def finalize(self):
        if len(self.values) == 0:
            return None
        return statistics.median(self.values)


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.create_aggregate("MEDIAN", 1, Median)

    for sql_path in sorted(glob.glob(os.path.join(SQL_DIR, "*.sql"))):
        name = os.path.basename(sql_path).replace(".sql", "")
        with open(sql_path) as f:
            query = f.read()

        result = pd.read_sql_query(query, conn)
        result.to_csv(os.path.join(OUTPUT_DIR, name + ".csv"), index=False)
        print(f"{name}: {len(result)} rows saved")

    conn.close()


if __name__ == "__main__":
    main()

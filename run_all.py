"""Run the whole project with one command:  python3 run_all.py

1. download the raw data from Kaggle
2. clean it and load it into SQLite
3. run every SQL query and save the results to outputs/
4. build the dashboard at docs/index.html
"""
import os
import sys

# Let Python find the scripts in the scripts/ folder.
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "scripts"))

import build_dashboard  # noqa: E402
import clean_and_load  # noqa: E402
import download_data  # noqa: E402
import run_queries  # noqa: E402

if __name__ == "__main__":
    print("\n[1/4] Download data")
    download_data.main()
    print("\n[2/4] Clean and load into SQLite")
    clean_and_load.main()
    print("\n[3/4] Run SQL queries")
    run_queries.main()
    print("\n[4/4] Build dashboard")
    build_dashboard.main()
    print("\nDone. Open docs/index.html in a browser.")

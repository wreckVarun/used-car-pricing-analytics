# Used Car Pricing Analytics

SQL analysis of 15,230 CarDekho used-car listings to help a used-car dealer make two everyday decisions:

1. **Which stock to acquire**: which cars sell often and hold their value?
2. **What price to list it at**: what do similar cars ask, and what is a gearbox, fuel type or extra 50,000 km worth?

**Live dashboard:** https://wreckvarun.github.io/used-car-pricing-analytics/

---

## The business problem

A dealer earns the gap between what they pay for a car and what they sell it for, minus the cost of holding it on the lot. Two things eat that margin:

- **Buying the wrong stock.** A car that few people want, or that loses value quickly, sits on the lot and gets cheaper every month.
- **Pricing it wrong.** List too high and the car doesn't move; list too low and the margin is gone.

This project uses public listing data to answer both questions with simple, explainable numbers (medians and peer comparisons, no machine learning).

## Dataset

- **Source:** [CarDekho Used Car Data](https://www.kaggle.com/datasets/manishkr1754/cardekho-used-car-data) on Kaggle (Indian used-car listings from cardekho.com).
- **Columns:** brand, model, age, km driven, seller type, fuel, transmission, mileage, engine, power, seats, asking price.
- **Size:** 1.4 MB CSV. It is downloaded by `scripts/download_data.py` and is not stored in this repo.

| Stage | Rows |
|---|---|
| Raw file | **15,411** |
| Removed: impossible value (0 seats) | 2 |
| Removed: exact duplicate listings | 167 |
| Removed: odometer above 500,000 km (e.g. 3,800,000 km on a 5-year-old car) | 12 |
| **Clean table used for analysis** | **15,230** (31 brands, 115 models) |

The source file has no blank cells, so "missing values" here means impossible values (0 seats) that were turned into missing and then dropped. 1,299 rows had truncated or duplicate model names that were fixed (for example `Grand` → `Grand i10`, BMW `3` → `3 Series`, `redi-GO` → `RediGO`). The full log is in [`outputs/cleaning_log.csv`](outputs/cleaning_log.csv).

## How to run it

Needs Python 3.9+.

```bash
pip3 install -r requirements.txt
python3 run_all.py
```

`run_all.py` runs four steps in order:

| Step | Script | Output |
|---|---|---|
| 1. Download | `scripts/download_data.py` | `data/raw/cardekho_dataset.csv` |
| 2. Clean + load | `scripts/clean_and_load.py` | `data/used_cars.db` (SQLite), `outputs/cleaning_log.csv` |
| 3. Run SQL | `scripts/run_queries.py` | one CSV per query in `outputs/` |
| 4. Dashboard | `scripts/build_dashboard.py` | `docs/index.html` (published with GitHub Pages) |

SQLite stands in for MySQL. Neither has a built-in `MEDIAN()`, so `run_queries.py` adds one in about ten lines of Python.

## SQL queries

| File | Question it answers |
|---|---|
| [`01_median_price_by_brand_model.sql`](sql/01_median_price_by_brand_model.sql) | What does each model typically sell for? |
| [`02_depreciation_by_age.sql`](sql/02_depreciation_by_age.sql) | How fast do prices fall with age? |
| [`03_price_vs_km.sql`](sql/03_price_vs_km.sql) | How much does km driven matter, once model and age are fixed? |
| [`04_fuel_transmission_price.sql`](sql/04_fuel_transmission_price.sql) | Median price by fuel and gearbox (simple view) |
| [`05_like_for_like_premium.sql`](sql/05_like_for_like_premium.sql) | Automatic and diesel premium for the same model and age |
| [`06_most_listed_segments.sql`](sql/06_most_listed_segments.sql) | Which model + age segments have the most listings? |
| [`07_value_retention_by_model.sql`](sql/07_value_retention_by_model.sql) | Which models hold their value best? |
| [`08_pricing_flags.sql`](sql/08_pricing_flags.sql) | Which listings are priced 25%+ above or below similar cars? |

## Key findings

**1. Age drives price: a car loses about a quarter of its value between years 2 and 5.**
The median asking price falls from ₹8.2 lakh at 2 years to ₹6.0 lakh at 5 years (73.5% of the 2-year price) and ₹3.4 lakh at 10 years (41%). After year 2 the median drops 7–16% every year. *(02_depreciation_by_age)*

**2. Buy mass-market Maruti and Hyundai models, be careful with German luxury cars.**
Comparing 7–9 year old cars with 2–4 year old cars of the same model, the Maruti Celerio keeps 78% of its value, the Hyundai Grand i10 76%, the Maruti Ertiga 72%, and the Alto and Wagon R about 70%. The Mercedes-Benz C-Class keeps only 38.5%, the E-Class 39.8%, the BMW X1 40% and the BMW 3 Series 42%. A luxury car on the lot loses value much faster. *(07_value_retention_by_model)*

**3. The most-traded stock is 4–6 year old hatchbacks and sedans.**
The busiest segments are the 4–6 year old Hyundai i20 (393 listings), Maruti Swift Dzire (374), Hyundai Grand i10 (329) and Honda City (323). All of the top 12 segments are mass-market models. The Grand i10, Alto, Wagon R and Swift are both high-volume and high-retention, which makes them the safest stock. *(06_most_listed_segments, 07)*

**4. Price on model and age first. Km matters much less, gearbox and fuel matter more.**
Against cars of the same model and age, a 0–20k km car is priced at 101.9 (100 = typical) and a 150k+ km car at 97.7: only about 4 points apart across the whole km range. In contrast, an automatic asks **12.2% more** than a manual of the same model and age (165 model-age groups, 7,690 listings), and a diesel **6.7% more** than a petrol (196 groups, 8,508 listings). The simple, unmatched view is misleading: diesel automatics have a median of ₹16.5 lakh against ₹4.2 lakh for petrol manuals, mostly because they are bigger, pricier models. *(03_price_vs_km, 04, 05)*

**5. About 1 in 25 listings is priced 25%+ under similar cars, and individual sellers are the best place to find them.**
13,822 listings have at least 5 peers (same model, age, fuel and gearbox). Of those, 571 (4.1%) are priced 25%+ below the peer median and 909 (6.6%) are 25%+ above it. Individual sellers list below market 6.4% of the time versus 2.8% for dealers, so private sellers are where acquisition bargains are most likely. *(08_pricing_flags)*

## Limitations

- **Asking prices, not sale prices.** The data shows what sellers asked, not what buyers paid.
- **No dates.** There is no listing or sale date, so "fastest-moving" uses the number of listings as a stand-in for demand. Days-on-lot would be the real measure.
- **One snapshot, one market.** The listings come from one scrape of an Indian website; prices change over time and by city, and the data has no city column.
- **Condition is unknown.** There is no data on accidents, service history, number of owners or trim level, all of which affect price. Some "below market" listings may be damaged cars or typing errors and need checking before buying.
- **Peer groups ignore km and trim.** The pricing flag compares a car only with the same model, age, fuel and gearbox. Small peer groups (5–10 cars) give rougher medians.
- **Model name fixes are manual.** Truncated names such as `Grand` were mapped to `Grand i10` by hand; the full list is in `scripts/clean_and_load.py`.
- **Small samples for luxury and rare models.** Most of the retention and premium numbers come from mass-market cars; luxury results rest on fewer listings.

## Project structure

```
used-car-pricing-analytics/
├── run_all.py               # runs everything with one command
├── requirements.txt
├── scripts/
│   ├── download_data.py     # step 1: get the CSV from Kaggle
│   ├── clean_and_load.py    # step 2: clean + load into SQLite
│   ├── run_queries.py       # step 3: run sql/*.sql, save CSVs
│   └── build_dashboard.py   # step 4: build docs/index.html
├── sql/                     # 8 analysis queries
├── outputs/                 # query results + cleaning log (CSV)
└── docs/index.html          # the dashboard (GitHub Pages)
```

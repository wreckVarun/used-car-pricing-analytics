-- Like-for-like price premium: automatic vs manual, and diesel vs petrol.
-- We only compare cars of the SAME model and SAME age, so the premium is not
-- just "automatics/diesels tend to be newer or bigger cars".
-- Step 1: for each model + age, get the median price of each version.
-- Step 2: keep groups with at least 3 listings of each version.
-- Step 3: report the median price ratio across those groups.

WITH gearbox AS (
    SELECT
        brand, model, vehicle_age,
        MEDIAN(CASE WHEN transmission_type = 'Automatic' THEN selling_price END) AS price_a,
        MEDIAN(CASE WHEN transmission_type = 'Manual'    THEN selling_price END) AS price_b,
        SUM(transmission_type = 'Automatic') AS n_a,
        SUM(transmission_type = 'Manual')    AS n_b
    FROM listings
    GROUP BY brand, model, vehicle_age
),

fuel AS (
    SELECT
        brand, model, vehicle_age,
        MEDIAN(CASE WHEN fuel_type = 'Diesel' THEN selling_price END) AS price_a,
        MEDIAN(CASE WHEN fuel_type = 'Petrol' THEN selling_price END) AS price_b,
        SUM(fuel_type = 'Diesel') AS n_a,
        SUM(fuel_type = 'Petrol') AS n_b
    FROM listings
    GROUP BY brand, model, vehicle_age
)

SELECT
    'Automatic vs Manual' AS comparison,
    COUNT(*)              AS matched_groups,
    SUM(n_a + n_b)        AS listings_compared,
    ROUND(100.0 * (MEDIAN(1.0 * price_a / price_b) - 1), 1) AS median_premium_pct
FROM gearbox
WHERE n_a >= 3 AND n_b >= 3

UNION ALL

SELECT
    'Diesel vs Petrol',
    COUNT(*),
    SUM(n_a + n_b),
    ROUND(100.0 * (MEDIAN(1.0 * price_a / price_b) - 1), 1)
FROM fuel
WHERE n_a >= 3 AND n_b >= 3;

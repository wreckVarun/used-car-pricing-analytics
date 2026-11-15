-- Which models hold their value best?
-- Compare the median price of 2-4 year old cars with 7-9 year old cars of the
-- same model. retention_pct = older price as a % of the younger price.
-- A high number means the model loses value slowly, which is lower risk for
-- a dealer holding it in stock.

WITH by_model AS (
    SELECT
        brand,
        model,
        COUNT(*) AS listings,
        SUM(vehicle_age BETWEEN 2 AND 4) AS young_listings,
        SUM(vehicle_age BETWEEN 7 AND 9) AS old_listings,
        MEDIAN(CASE WHEN vehicle_age BETWEEN 2 AND 4 THEN selling_price END) AS median_price_2_4_yrs,
        MEDIAN(CASE WHEN vehicle_age BETWEEN 7 AND 9 THEN selling_price END) AS median_price_7_9_yrs
    FROM listings
    GROUP BY brand, model
)

SELECT
    brand,
    model,
    listings,
    median_price_2_4_yrs,
    median_price_7_9_yrs,
    ROUND(100.0 * median_price_7_9_yrs / median_price_2_4_yrs, 1) AS retention_pct
FROM by_model
WHERE young_listings >= 10
  AND old_listings >= 10
ORDER BY retention_pct DESC;

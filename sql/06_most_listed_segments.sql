-- Fastest-moving segments, measured by number of listings.
-- The data has no "days to sell", so listing volume is used as a stand-in:
-- the cars that appear most often are the ones the market trades most.
-- A segment = brand + model + age band.

WITH segments AS (
    SELECT
        brand,
        model,
        CASE
            WHEN vehicle_age <= 3 THEN '0-3 yrs'
            WHEN vehicle_age <= 6 THEN '4-6 yrs'
            WHEN vehicle_age <= 9 THEN '7-9 yrs'
            ELSE '10+ yrs'
        END AS age_band,
        selling_price,
        km_driven
    FROM listings
)

SELECT
    brand,
    model,
    age_band,
    COUNT(*)                                                         AS listings,
    ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM listings), 2)     AS share_of_all_listings_pct,
    MEDIAN(selling_price)                                            AS median_price,
    MEDIAN(km_driven)                                                AS median_km
FROM segments
GROUP BY brand, model, age_band
ORDER BY listings DESC
LIMIT 20;

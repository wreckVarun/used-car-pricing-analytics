-- Does a higher odometer reading lower the price?
-- A raw comparison is misleading: high-km cars are also older and are more
-- often big diesel cars. So each listing is compared with the median price of
-- the SAME model at the SAME age (its "peers"). price_index = 100 means the
-- car is priced exactly like its peers; 90 means 10% cheaper.

WITH peer_median AS (
    SELECT brand, model, vehicle_age, MEDIAN(selling_price) AS peer_price
    FROM listings
    GROUP BY brand, model, vehicle_age
    HAVING COUNT(*) >= 5
),

indexed AS (
    SELECT
        l.km_driven,
        l.selling_price,
        100.0 * l.selling_price / p.peer_price AS price_index,
        CASE
            WHEN l.km_driven < 20000  THEN '0-20k'
            WHEN l.km_driven < 40000  THEN '20-40k'
            WHEN l.km_driven < 60000  THEN '40-60k'
            WHEN l.km_driven < 80000  THEN '60-80k'
            WHEN l.km_driven < 100000 THEN '80-100k'
            WHEN l.km_driven < 150000 THEN '100-150k'
            ELSE '150k+'
        END AS km_band
    FROM listings AS l
    JOIN peer_median AS p
        ON  l.brand = p.brand
        AND l.model = p.model
        AND l.vehicle_age = p.vehicle_age
)

SELECT
    km_band,
    COUNT(*)                       AS listings,
    MEDIAN(selling_price)          AS median_price,
    ROUND(MEDIAN(price_index), 1)  AS median_price_index
FROM indexed
GROUP BY km_band
ORDER BY MIN(km_driven);

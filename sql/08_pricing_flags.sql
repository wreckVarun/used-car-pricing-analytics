-- Flag listings priced well above or below similar cars.
-- "Similar cars" (peers) = same brand, model, age, fuel and gearbox.
-- We need at least 5 peers for a fair comparison.
--   price at least 25% under the peer median -> 'Below market' (possible buy)
--   price at least 25% over the peer median  -> 'Above market' (hard to sell)
--   anything in between                      -> 'In line'
-- No machine learning: just a median and two thresholds.

WITH peers AS (
    SELECT
        brand, model, vehicle_age, fuel_type, transmission_type,
        COUNT(*)              AS peer_count,
        MEDIAN(selling_price) AS peer_median_price
    FROM listings
    GROUP BY brand, model, vehicle_age, fuel_type, transmission_type
    HAVING COUNT(*) >= 5
)

SELECT
    l.listing_id,
    l.car_name,
    l.vehicle_age,
    l.km_driven,
    l.fuel_type,
    l.transmission_type,
    l.seller_type,
    l.selling_price,
    p.peer_count,
    p.peer_median_price,
    ROUND(100.0 * l.selling_price / p.peer_median_price, 1) AS price_vs_peers_pct,
    CASE
        WHEN l.selling_price <= 0.75 * p.peer_median_price THEN 'Below market'
        WHEN l.selling_price >= 1.25 * p.peer_median_price THEN 'Above market'
        ELSE 'In line'
    END AS price_flag
FROM listings AS l
JOIN peers AS p
    ON  l.brand = p.brand
    AND l.model = p.model
    AND l.vehicle_age = p.vehicle_age
    AND l.fuel_type = p.fuel_type
    AND l.transmission_type = p.transmission_type
ORDER BY price_vs_peers_pct;

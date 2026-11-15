-- Typical (median) listing price for each brand and model.
-- Median is used instead of average so a few very expensive cars
-- do not pull the number up.
-- Only models with at least 30 listings are shown, so the median is reliable.

SELECT
    brand,
    model,
    COUNT(*)              AS listings,
    MEDIAN(selling_price) AS median_price,
    MEDIAN(vehicle_age)   AS median_age_years,
    MEDIAN(km_driven)     AS median_km
FROM listings
GROUP BY brand, model
HAVING COUNT(*) >= 30
ORDER BY listings DESC;

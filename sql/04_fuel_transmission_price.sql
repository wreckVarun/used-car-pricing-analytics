-- Median price for each fuel type and gearbox combination.
-- This is the simple view. It mixes in age and model differences
-- (automatics are often newer or luxury cars); query 05 removes that.
-- Combinations with fewer than 30 listings are left out.

SELECT
    fuel_type,
    transmission_type,
    COUNT(*)              AS listings,
    MEDIAN(selling_price) AS median_price,
    MEDIAN(vehicle_age)   AS median_age_years
FROM listings
GROUP BY fuel_type, transmission_type
HAVING COUNT(*) >= 30
ORDER BY fuel_type, transmission_type;

-- How the typical price falls as cars get older.
-- Age 0 is skipped (only 5 listings). Cars 15+ years old are grouped together.
-- pct_of_age2_price: median price at this age as a % of the 2-year-old median.
-- Age 2 is the base because 1-year-old listings are few (221) and are mostly
-- small cheap hatchbacks, which makes their median look lower than age 2.

WITH by_age AS (
    SELECT
        CASE WHEN vehicle_age >= 15 THEN 15 ELSE vehicle_age END AS age_years,
        COUNT(*)              AS listings,
        MEDIAN(selling_price) AS median_price
    FROM listings
    WHERE vehicle_age >= 1
    GROUP BY 1
)

SELECT
    age_years,
    listings,
    median_price,
    ROUND(100.0 * median_price / (SELECT median_price FROM by_age WHERE age_years = 2), 1)
        AS pct_of_age2_price,
    ROUND(100.0 * (median_price - LAG(median_price) OVER (ORDER BY age_years))
          / LAG(median_price) OVER (ORDER BY age_years), 1)
        AS change_vs_prev_year_pct
FROM by_age
ORDER BY age_years;

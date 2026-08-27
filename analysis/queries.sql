-- ============================================================
-- CityAir Analytics Queries
-- ============================================================


-- 1. Latest reading for every city and pollutant

SELECT
    c.city_name,
    c.state,
    r.parameter,
    r.value,
    r.unit,
    r.measured_at

FROM readings r

JOIN cities c
    ON c.city_id = r.city_id

WHERE r.measured_at = (
    SELECT MAX(r2.measured_at)
    FROM readings r2
    WHERE r2.city_id = r.city_id
      AND r2.parameter = r.parameter
)

ORDER BY r.parameter, r.value DESC;


-- ============================================================
-- 2. Average pollutant concentration by city
-- ============================================================

SELECT
    c.city_name,
    c.state,
    r.parameter,
    ROUND(AVG(r.value), 2) AS avg_value,
    COUNT(*) AS observations

FROM readings r

JOIN cities c
    ON c.city_id = r.city_id

GROUP BY
    c.city_name,
    c.state,
    r.parameter

ORDER BY
    r.parameter,
    avg_value DESC;


-- ============================================================
-- 3. Daily PM2.5 trend
-- ============================================================

SELECT
    c.city_name,
    DATE(r.measured_at) AS day,
    ROUND(AVG(r.value), 2) AS avg_pm25

FROM readings r

JOIN cities c
    ON c.city_id = r.city_id

WHERE r.parameter = 'pm25'

GROUP BY
    c.city_name,
    DATE(r.measured_at)

ORDER BY
    day;


-- ============================================================
-- 4. Worst cities by PM2.5
-- ============================================================

SELECT
    c.city_name,
    ROUND(AVG(r.value), 2) AS avg_pm25

FROM readings r

JOIN cities c
    ON c.city_id = r.city_id

WHERE r.parameter = 'pm25'

GROUP BY c.city_name

ORDER BY avg_pm25 DESC;


-- ============================================================
-- 5. Data freshness
-- ============================================================

SELECT
    c.city_name,
    MAX(r.measured_at) AS latest_reading,
    COUNT(*) AS total_readings

FROM readings r

JOIN cities c
    ON c.city_id = r.city_id

GROUP BY c.city_name

ORDER BY latest_reading DESC;


-- ============================================================
-- 6. Pollutant coverage
-- ============================================================

SELECT
    parameter,
    COUNT(*) AS readings,
    COUNT(DISTINCT city_id) AS cities

FROM readings

GROUP BY parameter

ORDER BY readings DESC;


-- ============================================================
-- 7. Monitoring infrastructure
-- ============================================================

SELECT
    c.city_name,
    COUNT(DISTINCT l.location_id) AS locations,
    COUNT(DISTINCT s.sensor_id) AS sensors

FROM cities c

LEFT JOIN locations l
    ON l.city_id = c.city_id

LEFT JOIN sensors s
    ON s.location_id = l.location_id

GROUP BY c.city_name

ORDER BY sensors DESC;
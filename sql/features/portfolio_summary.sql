SELECT
    purpose,
    housing,
    COUNT(*) AS applications,
    SUM(defaulted) AS defaults,
    ROUND(AVG(defaulted)::NUMERIC, 4) AS observed_default_rate,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY credit_amount) AS median_credit_amount
FROM raw.credit_applications
GROUP BY purpose, housing
ORDER BY applications DESC, purpose, housing;


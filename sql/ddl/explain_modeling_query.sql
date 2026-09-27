EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT application_id, credit_amount, duration_months, defaulted
FROM raw.credit_applications
WHERE credit_amount BETWEEN 2500 AND 10000
ORDER BY duration_months;


-- Every query must return zero rows for a clean dataset.
SELECT 'invalid_target' AS check_name, COUNT(*) AS failures
FROM raw.credit_applications WHERE defaulted NOT IN (0, 1)
HAVING COUNT(*) > 0;

SELECT 'duplicate_business_key' AS check_name, COUNT(*) AS failures
FROM (
    SELECT source_name, source_row_id
    FROM raw.credit_applications
    GROUP BY source_name, source_row_id
    HAVING COUNT(*) > 1
) AS duplicates
HAVING COUNT(*) > 0;

SELECT 'invalid_numeric_domain' AS check_name, COUNT(*) AS failures
FROM raw.credit_applications
WHERE age NOT BETWEEN 18 AND 100
   OR credit_amount <= 0
   OR duration_months NOT BETWEEN 1 AND 120
HAVING COUNT(*) > 0;


CREATE OR REPLACE VIEW curated.credit_modeling AS
WITH portfolio_stats AS (
    SELECT
        purpose,
        COUNT(*) AS purpose_applications,
        AVG(credit_amount) AS purpose_avg_amount
    FROM raw.credit_applications
    GROUP BY purpose
), ranked AS (
    SELECT
        a.*,
        ROW_NUMBER() OVER (
            PARTITION BY a.purpose ORDER BY a.credit_amount DESC, a.application_id
        ) AS amount_rank_within_purpose,
        AVG(a.credit_amount) OVER (
            PARTITION BY a.purpose
        ) AS window_purpose_avg_amount
    FROM raw.credit_applications AS a
)
SELECT
    r.application_id,
    r.age,
    r.credit_amount::DOUBLE PRECISION AS credit_amount,
    r.duration_months,
    r.installment_rate,
    r.existing_credits,
    r.dependents,
    r.checking_status,
    r.credit_history,
    r.purpose,
    r.savings_status,
    r.employment_duration,
    r.housing,
    r.foreign_worker,
    CASE WHEN r.age < 25 THEN 'young' WHEN r.age < 55 THEN 'mid' ELSE 'senior' END AS age_band,
    r.credit_amount / NULLIF(r.duration_months, 0) AS monthly_credit_burden,
    r.credit_amount / NULLIF(ps.purpose_avg_amount, 0) AS amount_vs_purpose_avg,
    ps.purpose_applications,
    r.amount_rank_within_purpose,
    r.defaulted,
    r.source_name,
    r.source_row_id
FROM ranked AS r
JOIN portfolio_stats AS ps USING (purpose)
WHERE r.credit_amount > 0
  AND EXISTS (
      SELECT 1 FROM raw.credit_applications AS check_row
      WHERE check_row.application_id = r.application_id
  );


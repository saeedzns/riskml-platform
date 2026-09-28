# SQL implementation guide

- `alembic/versions/20260928_0001_initial.py` creates schemas, constraints, uniqueness, and indexes.
- `sql/transformations/001_modeling_view.sql` uses CTEs, grouped aggregates, a join, conditional age
  bands, correlated existence check, `NULLIF`, and window functions. It preserves `source_name` and
  `source_row_id` so canonical training can select one lineage deterministically.
- `sql/features/portfolio_summary.sql` demonstrates two-dimensional grouping, conditional target
  aggregation, and ordered-set median aggregation.
- `sql/quality/credit_applications.sql` contains zero-row quality assertions.
- `sql/ddl/explain_modeling_query.sql` is the reproducible query-plan probe.

The `(credit_amount, duration_months)` index supports amount-range filtering and leaves a small sort
on duration where needed. Actual planner choice depends on table size and selectivity; capture real
`EXPLAIN (ANALYZE, BUFFERS)` output during the PostgreSQL verification rather than claiming a speedup.

`risk_ml.data.training_data.load_curated_training_frame` is the sole canonical model-frame reader.
It queries this view with a bound source parameter and selects only the original 13 model features and
target. The view's whole-portfolio ratios, counts, and ranks demonstrate SQL analytics but do not enter
the model because they are computed before the train/test split.


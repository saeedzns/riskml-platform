# Repository instructions for coding agents

`CODEX_FINANCIAL_RISK_ML_PLATFORM_MASTER_PLAN.md` is the authoritative specification.

- Use Python 3.12 and the `src/risk_ml` package; notebooks are never production logic.
- Keep domain, data, features, modeling, monitoring, and API boundaries explicit.
- Preserve leakage defenses: split before learned transforms; never expose `defaulted` as a feature.
- Prefer parameterized SQL and migrations. All ingestion must be safe to rerun.
- Configuration comes from `RISK_ML_*` environment variables. Never commit secrets or raw datasets.
- Add or update tests and documentation with every behavior change.
- Run `make lint`, `make type`, and `make test`; run integration and Docker checks when relevant.
- Generated metrics must come from executable evaluation, never from hand-written claims.
- Record consequential architecture choices in `docs/adr`.


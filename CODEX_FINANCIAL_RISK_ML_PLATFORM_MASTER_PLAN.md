# Codex Master Execution Plan — Production Financial Risk / Fraud ML Platform

> **Mode:** Autonomous implementation specification for VS Code Codex Agent
> **Primary goal:** Build, verify, document, and prepare a portfolio-grade end-to-end structured-data ML platform.
> **Source direction:** Based on the portfolio/job-market research supplied by Saeed. The project exists specifically to fill visible portfolio gaps in SQL, PostgreSQL, tabular ML, feature engineering, MLflow, Airflow, FastAPI/Pydantic, monitoring/drift, cloud deployment, and SHAP.

---

## 0. AGENT OPERATING CONTRACT — READ FIRST

You are the principal software engineer, ML engineer, data scientist, MLOps engineer, tester, and technical writer for this repository.

Do **not** stop after scaffolding, planning, generating TODOs, or producing a demo notebook. Continue through the implementation phases below until every locally achievable Definition of Done item is satisfied, or until you encounter a genuine external blocker that requires a human credential, paid resource, account approval, or irreversible decision.

### Mandatory autonomous loop
For every milestone:
1. Inspect the current repository and environment before changing anything.
2. Write/update the implementation plan and identify dependencies.
3. Implement the smallest coherent production-quality increment.
4. Run formatting, linting, static checks, unit tests, integration tests, and relevant smoke tests.
5. If anything fails, diagnose the root cause. Do not merely suppress the failure.
6. Repair the implementation and rerun the failed checks.
7. Run the broader regression suite after the targeted fix.
8. Review the diff for security, data leakage, reproducibility, maintainability, and accidental generated artifacts/secrets.
9. Update documentation when behavior or architecture changes.
10. Commit the verified milestone with a meaningful conventional commit message when Git is available and the working tree is appropriate for committing.
11. Continue to the next milestone without asking for permission.

Do not declare success based on code inspection alone when an executable verification is possible.

### When you may stop and ask the human
Only stop for a blocker that cannot safely be solved locally, such as:
- GitHub authentication/authorization that is genuinely unavailable;
- Azure authentication, subscription/resource selection, billing approval, or secrets;
- an external dataset whose license/terms require human acceptance;
- a destructive operation with meaningful user data risk;
- a product/business choice with multiple materially different consequences and no safe default.

When blocked, finish every independent task first. Then write `BLOCKERS.md` containing the exact blocker, what is already complete, the minimum human action required, and the exact command/action to resume. Do not use a blocker in one area as a reason to abandon unrelated work.

### Truthfulness rules
Never claim any of the following unless directly verified:
- cloud deployment succeeded;
- CI passed remotely;
- a model achieved a metric that was not produced by the implemented evaluation pipeline;
- monitoring detects real production drift when only synthetic/offline simulation exists;
- an endpoint works if it has not been exercised;
- all tests pass if only a subset ran;
- a feature is production-ready when it is placeholder code.

Label simulations and local substitutes explicitly.

---

## 1. PROJECT IDENTITY

Choose a concise professional repository name unless the repository already has one. Preferred default:

`risk-ml-platform`

Suggested public title:

**RiskML Platform — Production Credit Risk & Fraud Machine Learning System**

One-line positioning:

> End-to-end structured-data ML platform using PostgreSQL/SQL, reproducible feature engineering, scikit-learn/gradient boosting, MLflow, Airflow, FastAPI, Docker, automated testing, drift monitoring, explainability, CI/CD, and Azure-ready infrastructure.

The system must demonstrate engineering depth, not maximize the number of technologies mentioned.

---

## 2. TARGET SKILL SIGNALS

The finished repository must make these skills visible through actual code, tests, configuration, and documentation:

**Core:** Python, SQL, PostgreSQL, pandas, NumPy, scikit-learn, XGBoost or LightGBM, feature engineering, model evaluation/calibration, FastAPI, Pydantic, pytest, Docker, Docker Compose, GitHub Actions.

**MLOps/data:** MLflow, Airflow, Alembic, data validation with Pandera or Great Expectations, SHAP, Evidently or an equivalent maintained drift/monitoring approach.

**Cloud:** Azure deployment design and deployable configuration. Perform a real deployment only if credentials/resources are available; otherwise verify configuration locally and document the exact deployment procedure without falsely claiming deployment.

**Optional only when justified:** Optuna, dbt, Power BI export layer, PySpark. Do not introduce Spark/Kubernetes merely for keyword collection.

---

## 3. PRODUCT SCOPE

Build an end-to-end risk-scoring platform around a legitimate public structured dataset suitable for credit/default/fraud classification.

### Dataset decision
Evaluate a small set of credible public datasets and select one based on:
- legal/public accessibility;
- clear target definition;
- sufficient structured features;
- class imbalance or realistic risk characteristics;
- manageable local size;
- ability to demonstrate leakage prevention and time/business-aware features where applicable.

Document the selection and rejected alternatives in an ADR. Never commit restricted or unnecessarily large raw data to Git.

If dataset download requires human acceptance, build a deterministic synthetic fixture and the full pipeline interface first, document the blocker, and continue all work that can be validated without the real data.

### Required user-facing capabilities
The finished system should support:
- reproducible ingestion into PostgreSQL;
- SQL-based transformations/modeling views or tables;
- validated feature generation;
- baseline and stronger model training;
- experiment tracking;
- model evaluation and calibration analysis;
- model artifact/version handling;
- SHAP-based explanation;
- REST risk scoring;
- health/readiness endpoints;
- batch scoring path;
- drift/data-quality reporting;
- orchestrated pipeline execution;
- local multi-service startup with Docker Compose;
- automated CI checks;
- Azure-ready deployment artifacts/documentation.

---

## 4. ENGINEERING PRINCIPLES

Use a maintainable `src/` Python package layout. Keep notebooks optional and exploratory only; production logic must live in importable modules.

Requirements:
- Python version pinned/documented.
- Dependency management reproducible. Prefer `pyproject.toml` and a lock strategy supported by the chosen tooling.
- Configuration via typed settings/environment variables; provide `.env.example`, never real secrets.
- Structured logging.
- Type hints on production interfaces.
- Clear domain/data/model/API boundaries.
- Database migrations via Alembic.
- Idempotent ingestion where practical.
- Deterministic random seeds where meaningful.
- No target leakage.
- No preprocessing fit on validation/test data.
- No hardcoded machine-specific absolute paths.
- No credentials in source control.
- Avoid premature microservices. Use service boundaries only where they improve the portfolio system.

Prefer boring, well-supported tools over unnecessary custom frameworks.

---

## 5. REPOSITORY BASELINE

Create or normalize the repository with at least:

```text
.
├── .github/workflows/
├── airflow/
├── alembic/
├── configs/
├── data/                  # ignored except tiny fixtures/README
├── docker/
├── docs/
│   ├── adr/
│   ├── architecture/
│   └── runbooks/
├── monitoring/
├── notebooks/             # optional exploration only
├── scripts/
├── sql/
│   ├── ddl/
│   ├── transformations/
│   ├── features/
│   └── quality/
├── src/risk_ml/
│   ├── api/
│   ├── data/
│   ├── db/
│   ├── features/
│   ├── modeling/
│   ├── monitoring/
│   └── services/
├── tests/
│   ├── unit/
│   ├── integration/
│   └── fixtures/
├── .env.example
├── .gitignore
├── AGENTS.md
├── ARCHITECTURE.md
├── CHANGELOG.md
├── CONTRIBUTING.md
├── Makefile or equivalent task runner
├── pyproject.toml
├── README.md
└── SECURITY.md
```

Adapt names if the implementation benefits, but preserve clear separation of concerns.

---

## 6. PHASE 1 — FOUNDATION & GOVERNANCE

### Tasks
- Initialize Git if needed.
- Create the GitHub repository if the authenticated environment supports it; otherwise prepare the local repo completely and record the one required human action.
- Establish `main` as the stable branch.
- Add `.gitignore` for Python, IDE, secrets, data, models, MLflow artifacts, Airflow runtime files, caches, coverage, and OS files.
- Add `AGENTS.md` containing repository-specific rules for future coding agents.
- Add `SECURITY.md` covering secrets, dependency handling, dataset privacy/licensing, API exposure, and vulnerability reporting.
- Add `ARCHITECTURE.md` with system boundaries and Mermaid diagrams.
- Add ADR template and initial ADRs for dataset, database, model stack, orchestration, experiment tracking, and deployment approach.
- Configure formatter/linter/type checking. Prefer Ruff for lint/format; use mypy or Pyright if practical.
- Configure pre-commit if it adds reliable value.
- Add task commands such as `make setup`, `make lint`, `make test`, `make test-integration`, `make up`, `make down`, `make train`, `make evaluate`.

### Verification gate
A fresh developer should be able to install the package and run basic quality checks from documented commands.

---

## 7. PHASE 2 — POSTGRESQL & SQL-FIRST DATA LAYER

SQL visibility is a primary hiring objective. Do not hide transformations entirely in pandas.

### Required SQL evidence
Repository SQL must meaningfully demonstrate:
- joins;
- aggregations and `GROUP BY`;
- CTEs;
- window functions;
- subqueries where appropriate;
- conditional expressions;
- time-based feature generation if dataset supports timestamps;
- data-quality queries;
- constraints/indexes;
- query-plan/index reasoning for at least one important query.

### Tasks
- Add PostgreSQL service to Docker Compose.
- Create normalized/raw and curated/modeling schemas as appropriate.
- Implement Alembic migrations.
- Implement ingestion from source data to PostgreSQL.
- Make ingestion rerunnable/idempotent where feasible.
- Build SQL transformations into a reproducible modeling dataset.
- Add SQL data-quality checks.
- Add indexes justified by query patterns.
- Use `EXPLAIN`/`EXPLAIN ANALYZE` on meaningful queries and document findings without inventing performance claims.
- Add integration tests against PostgreSQL.

### Verification gate
From a clean database, one documented command must migrate, ingest fixture/sample data, execute transformations, and produce the expected modeling dataset.

---

## 8. PHASE 3 — DATA VALIDATION & LEAKAGE DEFENSE

### Tasks
- Define data contracts/schema validation using Pandera or Great Expectations.
- Validate types, nullability, ranges, categorical domains, duplicates, target validity, and important business invariants.
- Explicitly identify possible leakage columns and leakage mechanisms.
- Implement train/validation/test splitting appropriate to the selected dataset; use time-aware splitting if the data semantics demand it.
- Fit all learned preprocessing on training data only.
- Add tests designed to fail if target leakage or train/test contamination is introduced.
- Produce a concise data-quality report.

### Verification gate
Intentionally malformed test fixtures must trigger validation failures; clean fixtures must pass.

---

## 9. PHASE 4 — FEATURE ENGINEERING

### Tasks
- Implement features in SQL and/or Python according to the correct layer.
- Use scikit-learn pipelines/column transformers for learned preprocessing.
- Handle missing values and categorical variables explicitly.
- Add domain-reasonable interaction/ratio/aggregation features only when justified.
- Ensure feature names and transformations are traceable.
- Test deterministic transformations.
- Document every major feature family and leakage rationale.

### Verification gate
Training and inference must share the same feature contract. Add a test preventing training-serving transformation skew for representative fixtures.

---

## 10. PHASE 5 — MODELING BASELINE & STRONGER MODEL

Do not jump directly to boosting.

### Baseline
Implement a logistic-regression baseline with a reproducible preprocessing pipeline.

### Stronger model
Implement XGBoost or LightGBM. Choose based on dependency stability and dataset fit; document the choice.

### Imbalance
Evaluate appropriate approaches such as class weights, threshold tuning, or imbalanced-learn techniques. Never apply resampling before splitting. Avoid SMOTE by default unless it is empirically justified.

### Hyperparameter optimization
Use Optuna only after a deterministic baseline exists. Bound the search so tests and local development remain practical.

### Required metrics
At minimum consider and implement those relevant to the task:
- ROC-AUC;
- PR-AUC / average precision;
- precision;
- recall;
- F1;
- confusion matrix;
- calibration/Brier score;
- threshold-dependent business trade-offs.

Accuracy alone is not an acceptable primary metric for imbalanced risk classification.

### Verification gate
Training must be reproducible enough to regenerate metrics from a fixed fixture/config, and evaluation must save machine-readable metrics plus human-readable plots/reports.

---

## 11. PHASE 6 — MLFLOW EXPERIMENT TRACKING

### Tasks
- Add MLflow service/configuration suitable for local Docker Compose operation.
- Track parameters, metrics, dataset/version metadata, code/config context, plots, and model artifacts.
- Establish model naming/versioning conventions.
- Make training runs identifiable and reproducible.
- Do not require a cloud MLflow service for local verification.
- Add tests around tracking integration where practical, with lightweight isolated configuration.

### Verification gate
A local training run should create an MLflow run containing expected parameters, metrics, and artifacts.

---

## 12. PHASE 7 — EXPLAINABILITY WITH SHAP

### Tasks
- Add global feature importance/explanation for the stronger model.
- Add local per-prediction explanation suitable for API/report use.
- Handle model-specific SHAP behavior correctly.
- Document limitations: SHAP explains model behavior, not causal effects.
- Add tests for explanation output schema and failure handling.

### Verification gate
Given a valid example, the explanation service returns stable structured output with feature names and contributions without crashing.

---

## 13. PHASE 8 — FASTAPI + PYDANTIC SERVING

### Required endpoints
Use sensible versioning, e.g. `/api/v1`.

Implement at least:
- `GET /health` — process liveness;
- `GET /ready` — dependencies/model readiness;
- `POST /api/v1/predict` — single prediction;
- `POST /api/v1/predict/batch` — bounded batch scoring;
- explanation support either embedded or through a dedicated endpoint.

### API requirements
- Typed Pydantic request/response models.
- Validation errors handled cleanly.
- Model loaded once per process rather than per request.
- Structured logs with request/correlation IDs where useful.
- Sensible timeouts/limits and payload constraints.
- No sensitive raw records in logs.
- OpenAPI documentation works.
- Version/model metadata included in responses where useful.

### Tests
- unit tests for service logic;
- FastAPI/TestClient endpoint tests;
- invalid payload tests;
- readiness behavior when model/database unavailable;
- representative prediction contract tests.

### Verification gate
Start the API locally and exercise endpoints with actual HTTP requests. Do not rely solely on unit tests.

---

## 14. PHASE 9 — AIRFLOW ORCHESTRATION

Use Airflow for meaningful orchestration, not as decorative configuration.

### Pipeline
Create a DAG representing appropriate steps such as:

`ingest -> validate -> transform -> feature checks -> train -> evaluate -> register/promote candidate -> monitoring baseline`

Separate expensive/manual promotion semantics if necessary.

### Requirements
- Tasks should call reusable application modules rather than duplicate business logic inside DAG files.
- Retries/timeouts should be sensible.
- Tasks should be idempotent where feasible.
- Configuration must be environment-driven.
- DAG import must be tested.
- Document local Airflow startup and triggering.

### Verification gate
At minimum verify DAG parsing/import and execute the underlying pipeline end-to-end locally. If practical in the environment, trigger the DAG and verify completion.

---

## 15. PHASE 10 — DOCKER & LOCAL PLATFORM

### Services
Compose only the services actually needed, likely:
- PostgreSQL;
- API;
- MLflow;
- Airflow components;
- optional monitoring/report service if justified.

### Requirements
- Multi-stage API image if beneficial.
- Non-root runtime user where practical.
- Health checks.
- Persistent named volumes for local state where appropriate.
- Environment variables through `.env`/Compose with safe examples.
- Avoid baking secrets/data/models into images.
- Pin base image versions sufficiently for reproducibility.
- Add `.dockerignore`.

### Verification gate
`docker compose config` must validate. When Docker is available, build images, start the stack, wait for health, run smoke tests, then shut it down cleanly.

---

## 16. PHASE 11 — MONITORING & DRIFT

Implement credible offline/local monitoring before making production claims.

### Monitor at least
- schema/data-quality failures;
- missingness changes;
- numeric/categorical feature distribution drift;
- prediction distribution;
- class/performance metrics when delayed labels are available;
- API operational telemetry/logging at a basic level.

Use Evidently if it is stable and appropriate; otherwise implement a simpler transparent statistical monitoring layer and document why.

### Tasks
- Persist a training/reference profile.
- Create a deliberately shifted synthetic/current dataset fixture.
- Generate drift report(s).
- Define thresholds and alert semantics in configuration.
- Test no-drift and drift scenarios.
- Clearly distinguish data drift, concept drift, and performance degradation.

### Verification gate
Automated tests must demonstrate that a controlled distribution shift is detected while a sufficiently similar fixture does not create an obvious false alarm under configured thresholds.

---

## 17. PHASE 12 — CI/CD WITH GITHUB ACTIONS

Create workflows that are useful and reasonably fast.

### Pull request / push CI
Include as appropriate:
- dependency installation/cache;
- Ruff format check;
- Ruff lint;
- type checking;
- unit tests;
- coverage threshold;
- integration tests with PostgreSQL service container;
- migration check;
- API tests;
- Airflow DAG import test;
- Docker build/config validation;
- secret scanning/dependency security checks using maintained tooling where practical.

Separate expensive jobs if needed.

### Deployment workflow
Prepare Azure deployment workflow with secure GitHub/Azure authentication design. Prefer OIDC/federated credentials over long-lived secrets when feasible. Do not place credentials in workflow files.

### Verification gate
Validate workflow YAML locally where possible and ensure commands match the same commands developers run locally. Remote CI status may only be claimed after GitHub actually runs it.

---

## 18. PHASE 13 — AZURE DEPLOYMENT

Target a pragmatic first cloud architecture rather than Kubernetes.

Preferred direction:
- Azure Container Apps **or** App Service for API;
- Azure Database for PostgreSQL;
- Azure Blob Storage for suitable artifacts/data objects;
- Azure Monitor / Application Insights where appropriate;
- GitHub Actions deployment.

### Tasks
- Create `docs/architecture/azure.md` with a Mermaid deployment diagram.
- Provide infrastructure/deployment configuration using a maintainable approach (Bicep/Terraform/Azure CLI scripts) if it can be validated confidently.
- Separate local and cloud configuration.
- Use managed identity/OIDC where possible.
- Define secret handling.
- Define database networking/access approach.
- Define logging/monitoring approach.
- Add deployment and rollback runbook.
- Add cost-conscious development defaults and note potentially billable resources.

### Real deployment rule
If Azure credentials and an approved subscription/resource context are already available, deploy and smoke-test the real service. If not, **do not fabricate deployment**. Finish and validate the deployment artifacts, then add the exact human authentication/resource step to `BLOCKERS.md`.

---

## 19. PHASE 14 — PORTFOLIO-GRADE DOCUMENTATION

The README must serve both a recruiter and an engineer.

### README structure
1. Clear project title and one-sentence value proposition.
2. Status badges only for real workflows/services.
3. Short architecture diagram.
4. What problem is being solved.
5. Why the dataset/modeling setup is realistic and its limitations.
6. Tech stack grouped by function.
7. Demonstrated skills, especially SQL/PostgreSQL and production ML.
8. Quick start.
9. Example API request/response.
10. Data pipeline and SQL examples.
11. Model evaluation with actual generated metrics only.
12. MLflow screenshot instructions or generated artifacts where appropriate.
13. SHAP explanation example.
14. Monitoring/drift example.
15. Testing/CI explanation.
16. Azure deployment status stated precisely.
17. Repository structure.
18. Security/privacy/limitations.
19. Roadmap limited to genuinely unfinished optional work.

### Additional docs
Create:
- architecture overview;
- data dictionary;
- model card;
- evaluation report generated from actual runs;
- SQL guide showing meaningful queries;
- local operations runbook;
- deployment runbook;
- monitoring runbook;
- ADRs.

Never hand-write impressive model metrics into documentation. Generate or update them from verified evaluation outputs.

---

## 20. PHASE 15 — SECURITY & ROBUSTNESS REVIEW

Before declaring completion, conduct a repository-wide audit.

Check for:
- committed secrets/tokens/passwords;
- `.env` accidentally tracked;
- unsafe pickle/model loading assumptions;
- SQL injection paths;
- unbounded API batch sizes;
- overly verbose logs containing input records;
- dependency vulnerabilities;
- Docker running unnecessarily as root;
- overly broad CORS;
- debug mode in production configuration;
- insecure default database exposure;
- path traversal/file upload risks if relevant;
- accidental personal/local paths;
- large data/model artifacts committed to Git;
- licenses/attribution for dataset and dependencies.

Fix findings that can be fixed locally. Document residual risks.

---

## 21. PHASE 16 — FINAL SELF-REVIEW & ADVERSARIAL TESTING

Act as a skeptical senior reviewer who did not write the code.

### Architecture review
Ask:
- Is every major component necessary?
- Are responsibilities cleanly separated?
- Is the project understandable without reading every file?
- Is the architecture more complex than the problem requires?

### ML review
Ask:
- Is there leakage?
- Is the split defensible?
- Are metrics appropriate for imbalance?
- Is calibration addressed?
- Are thresholds separated from raw probability estimation?
- Can training and inference preprocessing diverge?
- Are claims supported by generated evidence?

### Data/SQL review
Ask:
- Is SQL substantial or cosmetic?
- Are transformations reproducible?
- Are constraints and indexes justified?
- Can a clean DB be rebuilt automatically?

### Production review
Ask:
- Can a new developer run it?
- Can services recover from missing dependencies with understandable errors?
- Are health and readiness distinct?
- Are Docker and CI paths actually exercised?
- Are monitoring examples deterministic enough for tests?

Create `docs/FINAL_AUDIT.md` with findings, fixes made, residual limitations, and verification evidence.

---

## 22. REQUIRED TEST MATRIX

Implement a meaningful subset for each applicable row; do not create empty placeholder tests.

| Area | Required verification |
|---|---|
| Config | defaults, env overrides, invalid config |
| Data contracts | valid/invalid schema, null/range/domain checks |
| SQL | migrations, transformations, quality queries |
| Features | deterministic output, schema, leakage/skew protection |
| Models | fit/predict contract, serialization/loading, metrics |
| Evaluation | metric correctness on known fixtures |
| MLflow | run creation/logged artifacts where practical |
| SHAP | explanation schema and representative execution |
| API | health, readiness, valid/invalid predict, batch limits |
| Airflow | DAG import/structure, reusable pipeline calls |
| Monitoring | stable fixture vs shifted fixture |
| Docker | config/build/smoke test when Docker available |
| Integration | DB -> features -> model/service path |
| End-to-end | fixture ingestion -> transformation -> train -> score |

Use coverage as a signal, not a vanity metric. Set a reasonable enforced threshold after observing the codebase; do not exclude difficult production code merely to inflate coverage.

---

## 23. DEFINITION OF DONE

Do not mark the project complete until all locally achievable items below are true.

- [ ] Repository has coherent architecture and governance docs.
- [ ] Fresh environment setup is documented and reproducible.
- [ ] PostgreSQL starts locally and migrations apply from zero.
- [ ] Data ingestion works on the selected dataset or documented deterministic fixture.
- [ ] SQL transformations visibly demonstrate advanced SQL concepts.
- [ ] Data validation catches intentionally bad inputs.
- [ ] Leakage controls are documented and tested.
- [ ] Feature pipeline is shared/consistent between training and inference.
- [ ] Logistic regression baseline trains and evaluates.
- [ ] Stronger boosting model trains and evaluates.
- [ ] Appropriate imbalance metrics are generated.
- [ ] Calibration is evaluated.
- [ ] MLflow tracks a real local experiment.
- [ ] SHAP explanations execute.
- [ ] FastAPI starts and real HTTP smoke tests pass.
- [ ] Batch scoring is bounded and tested.
- [ ] Airflow DAG imports successfully and orchestration logic is exercised.
- [ ] Docker Compose configuration validates.
- [ ] Docker stack builds/runs/smoke-tests when Docker is available.
- [ ] Drift monitoring is tested with controlled shifted data.
- [ ] GitHub Actions workflows exist and use the repository's canonical commands.
- [ ] Azure deployment artifacts/runbook are complete and locally validated as far as possible.
- [ ] Real Azure deployment is either verified or explicitly marked blocked/not deployed.
- [ ] Security audit completed with no known committed secrets.
- [ ] Full local test suite passes.
- [ ] Lint/format/type checks pass.
- [ ] Documentation contains no unsupported performance/deployment claims.
- [ ] `docs/FINAL_AUDIT.md` records final verification evidence and residual limitations.
- [ ] Working tree is clean or any intentional uncommitted files are explained.

---

## 24. COMPLETION REPORT

At the very end, create `PROJECT_COMPLETION_REPORT.md` containing:

### A. What was built
Concise component inventory.

### B. Verified commands
Exact commands run and whether they passed.

### C. Test results
Counts and scopes from the final test runs. Do not invent numbers.

### D. Model results
Actual generated evaluation metrics, dataset/split context, and limitations.

### E. SQL evidence
List important SQL files and concepts demonstrated.

### F. Deployment status
State exactly one of:
- deployed and smoke-tested on Azure, with verifiable details; or
- Azure-ready but not deployed, with the external blocker/action required.

### G. Known limitations
Technical/data/model limitations that remain.

### H. Portfolio talking points
5–8 factual interview bullets supported by the repository.

### I. Resume skill line
A concise technology line containing only technologies actually implemented.

---

## 25. EXECUTION PRIORITY

When trade-offs arise, prioritize in this order:

1. correctness and leakage prevention;
2. reproducibility;
3. meaningful SQL/PostgreSQL evidence;
4. tested end-to-end ML behavior;
5. API/service reliability;
6. MLOps traceability;
7. monitoring;
8. cloud deployability;
9. documentation/presentation polish;
10. optional technologies.

Do not sacrifice correctness to make the stack look larger.

---

## 26. START NOW

Begin by inspecting the machine/repository context and available tooling. If no repository exists, create the project directory and initialize it. Establish the foundation, then proceed phase by phase.

Do **not** ask the user to approve routine implementation decisions. Make defensible engineering choices, document consequential decisions in ADRs, continuously test your work, repair failures, and proceed until the Definition of Done is satisfied or only genuine external blockers remain.

Before stopping for any reason, ask yourself:

> “Is there any independent implementation, testing, documentation, security review, or repair work I can still complete without human input?”

If yes, continue working.

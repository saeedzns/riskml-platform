# External and environment blockers

## GitHub repository and remote CI

GitHub CLI is not installed and no authenticated remote is available. Local workflows are complete,
but remote CI cannot truthfully be claimed. Minimum action: create an empty repository, then run
`git remote add origin <URL> && git push -u origin main` and verify both Actions workflows.

## Docker integration runtime

Docker CLI/Compose validates the configuration, but the Docker Linux engine is unavailable and Docker
Desktop is not installed at its standard location. Consequently PostgreSQL migrations/integration
tests and full-stack container build/health checks cannot run here. Minimum action: start/install a
compatible Docker engine, run `docker compose up -d postgres`, `python -m alembic upgrade head`, and
`python -m pytest -m integration`, followed by the stack smoke procedure in the local runbook.
Airflow 3.3 explicitly requires a POSIX runtime, so its source is parsed on Windows while its real DAG
import is assigned to the Linux CI/container path.

## Azure deployment

No Azure CLI credentials, approved subscription, resource naming context, region, or budget approval
is available. Artifacts are Azure-ready but not deployed. Follow `docs/runbooks/azure-deployment.md`
after an owner supplies those decisions; validate networking additions before provisioning billable
resources.


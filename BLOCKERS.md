# External and environment blockers

## GitHub remote CI verification

The repository now has an authenticated GitHub remote. Its first independent run passed PostgreSQL
integration and the dedicated Airflow DAG job, while exposing optional-dependency and clean-build-context
failures in the general quality and API-image jobs. Those root causes are repaired locally; the next
remote Actions run must complete before the overall CI workflow can be claimed green.

## Docker integration runtime

Docker CLI/Compose validates the configuration, but the local Docker Linux engine was unavailable for
this repair run (the Docker Desktop Linux named pipe does not exist). A temporary clean build context
with zero model-artifact entries was assembled, but the image build could not contact a daemon. The
next clean-checkout GitHub image build must verify the repaired Dockerfile; the PostgreSQL service job
already passed remotely. The full-stack smoke path is documented in the local runbook.
Airflow 3.3 explicitly requires a POSIX runtime, so its source is parsed on Windows while its real DAG
import is assigned to the Linux CI/container path.

## Azure deployment

No Azure CLI credentials, approved subscription, resource naming context, region, or budget approval
is available. Artifacts are Azure-ready but not deployed. Follow `docs/runbooks/azure-deployment.md`
after an owner supplies those decisions; validate networking additions before provisioning billable
resources.


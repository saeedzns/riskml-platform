# External and environment blockers

## Independent acceptance

Reported GitHub run #2 passed quality, PostgreSQL integration, and the dedicated Airflow DAG job, and
its API build passed the former missing-artifact failure. This acceptance repair changes the training
data path, integration test, Compose topology, and image matrix. A new GitHub Actions run and another
clean-room execution must verify them before acceptance can be claimed.

## Current Docker integration verification

An independent pre-repair clean-room run verified Docker Desktop Linux, PostgreSQL 16, MLflow,
migration from an empty database, and the expected schemas/tables. During this repair the Docker 29.8
engine initially responded and began building the API and CLI images, then its named pipe disappeared
before the builds completed. Compose configuration still validates. The new CLI image, modified
PostgreSQL integration test, full canonical training path, API startup, and prediction therefore await
the independent gates above.

## Native Windows policy

Windows Application Control blocks compiled extensions in the clean-room native environment: the
reported scikit-learn `_argkmin` import and this repair's explicit PostgreSQL test attempt both failed
when policy blocked `psycopg_binary.pq`. Security policy and dependency versions must not be weakened
to evade it. Use the documented Linux Compose CLI path. Airflow 3.3 likewise requires a POSIX runtime;
native Windows only parses its source while Linux CI performs the runtime import.

## Azure deployment

No Azure CLI credentials, approved subscription, resource naming context, region, or budget approval
is available. Artifacts are Azure-ready but not deployed. Follow `docs/runbooks/azure-deployment.md`
after an owner supplies those decisions; validate networking additions before provisioning billable
resources.


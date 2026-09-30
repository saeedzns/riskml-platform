# External and environment blockers

The local/containerized portfolio path has completed independent clean-room acceptance, and GitHub
Actions run #7 passed. The remaining items below are environment or optional cloud-deployment
constraints, not blockers to the verified portfolio project.

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


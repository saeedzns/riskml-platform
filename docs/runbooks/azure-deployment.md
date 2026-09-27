# Azure deployment and rollback runbook

## Prerequisites

An owner must select an approved subscription/region and budget, install Azure CLI/Bicep, and create a
GitHub federated identity constrained to the deployment environment. Configure repository variables
listed in `.github/workflows/deploy-azure.yml`; keep the PostgreSQL bootstrap password in an
environment secret and rotate it after managed access is established.

Validate without provisioning:

```bash
az bicep build --file infra/main.bicep
az deployment sub what-if --location REGION --template-file infra/main.bicep \
  --parameters environmentName=dev location=REGION postgresAdminLogin=ADMIN
```

Before deployment, add VNet delegation/private endpoints and Key Vault policy appropriate to the
organization; the template deliberately refuses public database access. Build, scan, and push an
immutable API image, then dispatch the workflow with its digest-derived tag. Apply migrations as a
one-shot job before shifting traffic. Verify `/health`, `/ready`, a canary prediction, logs, and metrics.

## Rollback

Container Apps keeps revisions. Identify the last healthy image/revision, activate it, and direct 100%
traffic to it. Database migrations must be backward compatible; restore a point-in-time backup into a
new server for destructive data rollback. Never roll credentials back—rotate them.


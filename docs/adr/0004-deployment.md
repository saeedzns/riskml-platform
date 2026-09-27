# ADR 0004: Azure Container Apps deployment target

- Status: Accepted
- Date: 2026-09-28

## Context

The API needs a pragmatic Azure target with autoscaling and OIDC-based CI/CD, without Kubernetes
operations. PostgreSQL and artifacts need managed services.

## Decision

Target Azure Container Apps, Azure Database for PostgreSQL Flexible Server, Blob Storage, Key Vault,
Log Analytics, and Application Insights. Provision with Bicep and deploy from GitHub Actions using
federated credentials. PostgreSQL uses restricted networking and TLS.

## Consequences

Artifacts are reviewable without cloud access and development defaults can scale to zero where
supported. Provisioning is billable and remains blocked until an owner authenticates and selects an
approved subscription, region, globally unique names, and budget.


# ADR 0001: Modular monolith with service-backed infrastructure

- Status: Accepted
- Date: 2026-09-28

## Context

The portfolio must demonstrate data, ML, API, orchestration, and operational boundaries without
creating costly distributed-system failure modes for one scoring domain.

## Decision

Use one typed Python package and separate PostgreSQL, MLflow, and Airflow runtime services. Business
logic remains importable and is called by CLI, DAG, and API adapters.

## Consequences

Tests and local workflows stay direct. Components can later separate behind stable interfaces, but
independent scaling and fault isolation are intentionally limited today.


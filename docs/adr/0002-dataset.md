# ADR 0002: UCI Statlog German Credit with deterministic fixture

- Status: Accepted
- Date: 2026-09-28

## Context

Candidates included UCI Statlog German Credit, UCI Default of Credit Card Clients, and the Kaggle
Home Credit dataset. The project needs public legal access, a clear binary target, mixed structured
features, manageable size, and credible imbalance without click-through terms.

## Decision

Use the UCI Statlog German Credit domain and feature semantics. UCI provides 1,000 observations under
CC BY 4.0 with a good/bad credit target. Reject Home Credit because distribution requires Kaggle
terms and is unnecessarily large; reject Default of Credit Card Clients because its fields are more
opaque and encourage questionable month-to-month leakage narratives. A seeded, source-compatible
synthetic fixture is the default for deterministic offline tests. Real UCI ingestion is an explicit
operator command and raw downloads remain ignored.

## Consequences

The dataset is small, historical, German, and has no event timestamp; random stratified splitting is
therefore used and temporal claims are forbidden. It is educational, not suitable for lending
decisions. Protected-attribute and fairness review remain necessary before any real use.


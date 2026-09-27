# Monitoring runbook

Run `python -m risk_ml.cli monitor` to create `artifacts/drift-report.json`. Numeric features use
population stability index with a 0.20 threshold; categorical features use total variation distance
with a 0.15 threshold; a missingness change above 0.10 also alerts. These are configurable function
parameters and initial engineering thresholds, not statistically universal constants.

An alert means one or more input distributions changed. It does not prove concept drift. Investigate
source/schema changes, segment composition, missingness, and prediction distribution. If delayed
labels exist, separately compare ROC-AUC, average precision, Brier score, recall, and business cost.
Retrain only after validating data and comparing a candidate against the champion; never automate
promotion solely because drift was detected.

Run `python -m risk_ml.cli monitor --simulate-shift --output artifacts/drift-shifted.json` for the
explicit offline alert demonstration. The command multiplies credit amounts and collapses checking
status in a synthetic current population; it is a simulation, not observed production drift.


# Model card: synthetic credit-default classifier

## Intended use

This educational model demonstrates a production ML workflow on deterministic synthetic data modeled
after UCI German Credit fields. It may support engineering demonstrations and offline experiments. It
must not approve, deny, price, or otherwise influence real credit.

## Models and evaluation

The baseline is class-weighted logistic regression. The comparator is regularized XGBoost. Both share
one fitted preprocessing pipeline and a fixed seeded stratified 75/25 split. Evaluation reports
ROC-AUC, average precision, Brier score, precision, recall, F1, and confusion matrix. The synthetic
fixture and small sample make estimates unstable; no external or temporal validation exists.

## Risks and limitations

The source domain is historical and geographically narrow. `foreign_worker` and age can encode
protected or proxy attributes; their presence illustrates schema handling, not acceptable lending
practice. Fairness metrics, adverse-action compliance, causal validity, human review, and governance
are not implemented. SHAP explanations describe model behavior and are not causal reasons.

Verified run metrics are generated in `artifacts/metrics-*.json` and summarized in the completion
report; this document intentionally does not duplicate mutable numbers.


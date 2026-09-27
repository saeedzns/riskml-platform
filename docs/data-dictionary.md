# Data dictionary

The deterministic fixture mirrors a documented subset of UCI German Credit semantics. It is synthetic
and contains no people. `defaulted=1` is an adverse credit outcome generated from a seeded probability;
it is never an input feature.

| Field | Type | Meaning |
|---|---|---|
| age | integer | Applicant age, 18–100 |
| credit_amount | float | Requested credit amount in dataset-relative currency units |
| duration_months | integer | Contract duration |
| installment_rate | integer | Ordinal disposable-income installment band, 1–4 |
| existing_credits | integer | Existing credit count band, 1–4 |
| dependents | integer | Supported-person count band, 1–2 |
| checking_status | category | Checking-account balance band |
| credit_history | category | Prior repayment-history band |
| purpose | category | Coarse credit purpose |
| savings_status | category | Savings balance band |
| employment_duration | category | Employment tenure band |
| housing | category | Rent, own, or free arrangement |
| foreign_worker | boolean | Historical dataset attribute; fairness-sensitive |
| defaulted | binary | Synthetic adverse outcome target |

SQL-only derived columns such as `purpose_default_rate` are for analysis and are deliberately excluded
from the deployed model because target aggregates require out-of-fold treatment to avoid leakage.


# Verified data-quality report

The official-client download for UCI dataset 144 produced 1,000 rows and 14 mapped columns: 13 model
inputs plus the target. The verified mapped file contained zero missing cells, zero fully duplicated
rows, 300 defaults (30%), and ages from 19 to 75.

Pandera enforces numeric ranges, target domain, categorical domains, nullability, unique column names,
and type coercion. PostgreSQL independently enforces primary/business keys, a record hash, range and
target checks, and not-null constraints. SQL assertions cover invalid targets, duplicate source keys,
and numeric domains. Tests deliberately introduce invalid age, amount, purpose, target, and duplicate
columns and verify rejection.

Identifiers, target, repayment status, loss amount, and collection status are forbidden as model
features. Target-derived SQL aggregates are not present in the modeling view. The dataset has no
reliable event time, so a seeded stratified split is used and no temporal-validation claim is made.


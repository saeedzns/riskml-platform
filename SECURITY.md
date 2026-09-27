# Security policy

Report vulnerabilities privately to the repository owner; do not open a public issue containing an
exploit or secret. Supported code is the latest `main` branch.

Secrets belong in environment variables or a managed secret store. `.env`, credentials, private
keys, raw customer data, model stores, and MLflow state are ignored. Development passwords in
`.env.example` and Compose are intentionally local-only and must be replaced outside a private
developer machine. Production database access should use TLS, private networking, least privilege,
and managed identity where supported.

Only public, attributed datasets or deterministic synthetic fixtures may be used. Do not ingest
personal or regulated records without legal approval, minimization, retention, and access controls.
Model artifacts are trusted inputs: this project loads joblib artifacts only from an operator-set
local path and does not accept uploads. Python pickle/joblib files can execute code and must never be
loaded from untrusted sources.

Dependencies are bounded in `pyproject.toml`; review automated vulnerability results before release.
The API does not log request bodies, bounds batch sizes, and exposes no permissive CORS default.


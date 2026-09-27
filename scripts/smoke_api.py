"""Exercise a running API over real HTTP."""

import json
import urllib.request

from risk_ml.data.fixture import generate_fixture

BASE_URL = "http://127.0.0.1:8000"


def request(path: str, payload: dict[str, object] | None = None) -> dict[str, object]:
    body = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(  # noqa: S310 -- fixed local HTTP base URL
        f"{BASE_URL}{path}",
        data=body,
        headers={"content-type": "application/json"} if body else {},
        method="POST" if body else "GET",
    )
    with urllib.request.urlopen(req, timeout=10) as response:  # noqa: S310
        return json.loads(response.read())


if __name__ == "__main__":
    record = generate_fixture(1).drop(columns=["defaulted"]).iloc[0].to_dict()
    print(
        json.dumps({"health": request("/health"), "prediction": request("/api/v1/predict", record)})
    )

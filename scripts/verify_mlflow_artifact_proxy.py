from __future__ import annotations

import tempfile
import uuid
from pathlib import Path

import mlflow
from mlflow import MlflowClient

TRACKING_URI = "http://mlflow:5000"
ARTIFACT_NAME = "mlflow-proxy-check.txt"
ARTIFACT_CONTENT = "artifact proxy verified\n"


def main() -> None:
    mlflow.set_tracking_uri(TRACKING_URI)
    client = MlflowClient(tracking_uri=TRACKING_URI)
    assert client.get_experiment_by_name("Default") is not None
    experiment_id = mlflow.create_experiment(f"ci-artifact-proxy-{uuid.uuid4().hex}")

    with tempfile.TemporaryDirectory() as artifact_dir:
        artifact_file = Path(artifact_dir) / ARTIFACT_NAME
        artifact_file.write_text(ARTIFACT_CONTENT, encoding="utf-8")
        with mlflow.start_run(experiment_id=experiment_id) as run:
            mlflow.log_artifact(str(artifact_file))
            artifact_uri = mlflow.get_artifact_uri()

    assert artifact_uri.startswith("mlflow-artifacts:/"), artifact_uri
    assert ARTIFACT_NAME in {artifact.path for artifact in client.list_artifacts(run.info.run_id)}
    with tempfile.TemporaryDirectory() as download_dir:
        downloaded = client.download_artifacts(
            run.info.run_id,
            ARTIFACT_NAME,
            download_dir,
        )
        assert Path(downloaded).read_text(encoding="utf-8") == ARTIFACT_CONTENT

    print(f"verified proxied artifact URI: {artifact_uri}")


if __name__ == "__main__":
    main()

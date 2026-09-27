import ast
import importlib.util
import os
from pathlib import Path

import pytest


def test_airflow_dag_source_parses() -> None:
    source = Path("airflow/dags/risk_ml_pipeline.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    assert any(isinstance(node, ast.With) for node in ast.walk(tree))


@pytest.mark.skipif(os.name == "nt", reason="Airflow runtime requires a POSIX environment")
def test_airflow_dag_import_and_structure() -> None:
    pytest.importorskip("airflow.providers.standard")
    path = Path("airflow/dags/risk_ml_pipeline.py")
    spec = importlib.util.spec_from_file_location("risk_ml_pipeline", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert module.dag.dag_id == "risk_ml_training_pipeline"
    assert {task.task_id for task in module.dag.tasks} == {
        "ingest",
        "validate",
        "transform",
        "train_evaluate_register",
        "monitoring_baseline",
    }

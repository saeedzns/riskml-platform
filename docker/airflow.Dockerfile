FROM apache/airflow:3.3.2-python3.12
COPY --chown=airflow:root pyproject.toml README.md /opt/risk-ml/
COPY --chown=airflow:root src /opt/risk-ml/src
RUN pip install --no-cache-dir /opt/risk-ml


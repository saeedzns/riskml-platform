FROM python:3.12.11-slim
ARG MLFLOW_VERSION=3.16.1
RUN python -m pip install --no-cache-dir "mlflow==${MLFLOW_VERSION}" "psycopg[binary]>=3.2,<4"
RUN groupadd --system mlflow && useradd --system --gid mlflow --home /mlflow mlflow
WORKDIR /mlflow
RUN mkdir -p /mlflow/artifacts && chown -R mlflow:mlflow /mlflow
USER mlflow
EXPOSE 5000
CMD ["mlflow", "server", "--host", "0.0.0.0", "--port", "5000", "--backend-store-uri", "sqlite:////mlflow/mlflow.db", "--default-artifact-root", "/mlflow/artifacts"]


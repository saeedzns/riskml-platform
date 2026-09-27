FROM python:3.12.11-slim AS builder
WORKDIR /build
COPY pyproject.toml README.md ./
COPY src ./src
RUN python -m pip install --no-cache-dir --prefix=/install .

FROM python:3.12.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
RUN groupadd --system riskml && useradd --system --gid riskml --home /app riskml
WORKDIR /app
COPY --from=builder /install /usr/local
COPY --chown=riskml:riskml src ./src
USER riskml
EXPOSE 8000
HEALTHCHECK --interval=15s --timeout=3s --retries=5 CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health', timeout=2)"
CMD ["uvicorn", "risk_ml.api.app:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000"]


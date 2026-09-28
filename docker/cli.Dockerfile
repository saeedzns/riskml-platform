FROM python:3.12.11-slim AS builder
WORKDIR /build
COPY pyproject.toml README.md ./
COPY src ./src
RUN python -m pip install --no-cache-dir --prefix=/install .

FROM python:3.12.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 HOME=/tmp MPLCONFIGDIR=/tmp/matplotlib
RUN groupadd --gid 1000 riskml && useradd --uid 1000 --gid riskml --home-dir /app --create-home riskml
WORKDIR /app
COPY --from=builder /install /usr/local
COPY --chown=riskml:riskml src ./src
COPY --chown=riskml:riskml alembic ./alembic
COPY --chown=riskml:riskml alembic.ini ./alembic.ini
USER riskml
CMD ["risk-ml", "--help"]

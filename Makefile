.PHONY: setup format lint type test test-integration verify migrate ingest transform train evaluate monitor api smoke up down

PYTHON ?= python

setup:
	$(PYTHON) -m pip install -e ".[dev]"

format:
	$(PYTHON) -m ruff format .
	$(PYTHON) -m ruff check --fix .

lint:
	$(PYTHON) -m ruff format --check .
	$(PYTHON) -m ruff check .

type:
	$(PYTHON) -m mypy

test:
	$(PYTHON) -m pytest -m "not integration" --cov --cov-report=term-missing

test-integration:
	$(PYTHON) -m pytest -m integration

verify: lint type test

migrate:
	$(PYTHON) -m alembic upgrade head

ingest:
	$(PYTHON) -m risk_ml.cli ingest

transform:
	$(PYTHON) -m risk_ml.cli transform

train:
	$(PYTHON) -m risk_ml.cli train --model all

evaluate:
	$(PYTHON) -m risk_ml.cli evaluate

monitor:
	$(PYTHON) -m risk_ml.cli monitor

api:
	$(PYTHON) -m uvicorn risk_ml.api.app:create_app --factory --host 0.0.0.0 --port 8000

smoke:
	$(PYTHON) scripts/smoke_api.py

up:
	docker compose up -d --build

down:
	docker compose down


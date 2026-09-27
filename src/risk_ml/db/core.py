"""SQLAlchemy engine and SQL execution helpers."""

from pathlib import Path

from sqlalchemy import Engine, create_engine, text

from risk_ml.config import get_settings


def create_db_engine(url: str | None = None) -> Engine:
    """Build a future-style pooled engine."""

    return create_engine(url or get_settings().database_url, pool_pre_ping=True)


def execute_sql_file(engine: Engine, path: Path) -> None:
    """Execute a trusted repository SQL file transactionally."""

    sql = path.read_text(encoding="utf-8")
    with engine.begin() as connection:
        connection.execute(text(sql))

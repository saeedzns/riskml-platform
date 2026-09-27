"""Create raw, curated, and monitoring schemas.

Revision ID: 20260928_0001
Revises:
"""

from alembic import op

revision = "20260928_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS raw")
    op.execute("CREATE SCHEMA IF NOT EXISTS curated")
    op.execute("CREATE SCHEMA IF NOT EXISTS monitoring")
    op.execute(
        """
        CREATE TABLE raw.credit_applications (
            application_id UUID PRIMARY KEY,
            source_name TEXT NOT NULL,
            source_row_id INTEGER NOT NULL,
            record_hash CHAR(64) NOT NULL UNIQUE,
            age INTEGER NOT NULL CHECK (age BETWEEN 18 AND 100),
            credit_amount NUMERIC(12,2) NOT NULL CHECK (credit_amount > 0),
            duration_months INTEGER NOT NULL CHECK (duration_months BETWEEN 1 AND 120),
            installment_rate INTEGER NOT NULL CHECK (installment_rate BETWEEN 1 AND 4),
            existing_credits INTEGER NOT NULL CHECK (existing_credits BETWEEN 1 AND 4),
            dependents INTEGER NOT NULL CHECK (dependents BETWEEN 1 AND 2),
            checking_status TEXT NOT NULL,
            credit_history TEXT NOT NULL,
            purpose TEXT NOT NULL,
            savings_status TEXT NOT NULL,
            employment_duration TEXT NOT NULL,
            housing TEXT NOT NULL,
            foreign_worker BOOLEAN NOT NULL,
            defaulted SMALLINT NOT NULL CHECK (defaulted IN (0, 1)),
            ingested_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            UNIQUE (source_name, source_row_id)
        )
        """
    )
    op.execute(
        "CREATE INDEX ix_credit_applications_target ON raw.credit_applications(defaulted)"
    )
    op.execute(
        "CREATE INDEX ix_credit_applications_amount_duration "
        "ON raw.credit_applications(credit_amount, duration_months)"
    )
    op.execute(
        """
        CREATE TABLE monitoring.predictions (
            prediction_id UUID PRIMARY KEY,
            model_version TEXT NOT NULL,
            probability DOUBLE PRECISION NOT NULL CHECK (probability BETWEEN 0 AND 1),
            predicted_default SMALLINT NOT NULL CHECK (predicted_default IN (0, 1)),
            created_at TIMESTAMPTZ NOT NULL DEFAULT now()
        )
        """
    )


def downgrade() -> None:
    op.execute("DROP SCHEMA IF EXISTS monitoring CASCADE")
    op.execute("DROP SCHEMA IF EXISTS curated CASCADE")
    op.execute("DROP SCHEMA IF EXISTS raw CASCADE")


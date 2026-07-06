"""Baseline schema.

Creates every table defined on the ORM ``Base.metadata``. Using create_all for
the initial revision keeps the baseline in lockstep with the models; subsequent
schema changes should use ``alembic revision --autogenerate`` as normal.

Revision ID: 0001_initial
Revises:
Create Date: 2026-07-06
"""

from alembic import op

from app.db.base import Base
import app.models  # noqa: F401 - register all tables on Base.metadata

# revision identifiers, used by Alembic.
revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    Base.metadata.create_all(bind=op.get_bind())


def downgrade() -> None:
    Base.metadata.drop_all(bind=op.get_bind())

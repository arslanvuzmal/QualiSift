"""
SQLAlchemy declarative base and portable column types.

All ORM models inherit from ``Base``. The portable column types defined here
let the *same* models run on PostgreSQL in production (where ``JSONB`` and the
native ``UUID`` type give the best indexing/performance) and on SQLite locally
or in CI (where those Postgres-only types do not exist).
"""

from sqlalchemy import JSON, Uuid
from sqlalchemy.dialects.postgresql import JSONB as _PostgresJSONB
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    Declarative base class for all SQLAlchemy models.

    This base class provides common functionality and metadata
    for all database models in the application.
    """

    pass


# --- Portable column types -------------------------------------------------
# ``JSONType`` renders as PostgreSQL ``JSONB`` (binary, indexable) in
# production and as generic ``JSON`` on every other dialect (e.g. SQLite),
# so a Postgres-less local/CI environment can still create the schema.
JSONType = JSON().with_variant(_PostgresJSONB, "postgresql")

# ``PortableUUID`` is SQLAlchemy 2.0's dialect-aware UUID type: native
# ``UUID`` on PostgreSQL, ``CHAR(32)`` on SQLite. Models keep calling it as
# ``UUID(as_uuid=True)`` via an import alias, so their bodies are unchanged.
PortableUUID = Uuid

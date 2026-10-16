"""Temporary PostgreSQL schema; no fall-through to public business tables."""

from contextlib import contextmanager
from uuid import uuid4

from sqlalchemy import text

from app import model_registry  # noqa: F401 — CLI must register all tables before cloning
from app.database import _evaluation_schema, engine
from app.models import Base
from app.perception.media import MediaIngestionService
from app.perception.models import MediaAsset
from app.seed import seed_demo


@contextmanager
def scenario_database(run_id=None):
    schema = "nova_eval_" + (run_id or uuid4()).hex
    tables = [
        t
        for t in Base.metadata.sorted_tables
        if not t.name.startswith(("evaluation_", "experiment_"))
    ]
    with engine.begin() as connection:
        connection.execute(text(f'CREATE SCHEMA "{schema}"'))
        Base.metadata.create_all(
            connection.execution_options(schema_translate_map={None: schema}),
            tables=tables,
            checkfirst=False,
        )
    from app.security.identity import principal

    identity_token = principal.set(None)
    token = _evaluation_schema.set(schema)
    try:
        yield schema
    finally:
        _evaluation_schema.reset(token)
        principal.reset(identity_token)
        with engine.begin() as connection:
            connection.execute(text(f'DROP SCHEMA IF EXISTS "{schema}" CASCADE'))


def reset_scenario(schema):
    from sqlalchemy import select

    from app.database import SessionLocal

    # Only media owned by this temporary schema is removed; demo volume records are untouched.
    with SessionLocal() as session:
        for media in session.scalars(select(MediaAsset)):
            MediaIngestionService().path(media).unlink(missing_ok=True)
    tables = [
        t
        for t in Base.metadata.sorted_tables
        if not t.name.startswith(("evaluation_", "experiment_"))
    ]
    with engine.begin() as connection:
        connection.execute(text("TRUNCATE " + ",".join(f'"{schema}"."{t.name}"' for t in tables)))
    seed_demo()


def cleanup_interrupted_schema(run_id):
    """Only server-generated run UUID namespaces; never enumerate/drop unrelated schemas."""
    schema = "nova_eval_" + run_id.hex
    with engine.begin() as connection:
        exists = connection.scalar(
            text("SELECT EXISTS (SELECT 1 FROM pg_namespace WHERE nspname=:name)"), {"name": schema}
        )
    if not exists:
        return
    token = _evaluation_schema.set(schema)
    try:
        from sqlalchemy import select

        from app.database import SessionLocal

        with SessionLocal() as session:
            for media in session.scalars(select(MediaAsset)):
                MediaIngestionService().path(media).unlink(missing_ok=True)
    finally:
        _evaluation_schema.reset(token)
    with engine.begin() as connection:
        connection.execute(text(f'DROP SCHEMA IF EXISTS "{schema}" CASCADE'))

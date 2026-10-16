import re
from collections.abc import Generator
from contextvars import ContextVar

from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker

from app.config import settings

engine = create_engine(settings.database_url, hide_parameters=True, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


def get_session() -> Generator[Session]:
    with SessionLocal() as session:
        yield session


# Evaluation scopes are server-owned ContextVars, never request headers/parameters.
# Checkout covers both SessionLocal and services with dedicated advisory-lock connections.

_evaluation_schema = ContextVar("nova_evaluation_schema", default=None)


@event.listens_for(engine, "checkout")
def evaluation_search_path(dbapi_connection, connection_record, connection_proxy):
    schema = _evaluation_schema.get()
    if schema is not None and not re.fullmatch(r"nova_eval_[0-9a-f]{32}", schema):
        raise ValueError("Invalid server evaluation namespace")
    prior = dbapi_connection.autocommit
    dbapi_connection.autocommit = True
    try:
        with dbapi_connection.cursor() as cursor:
            cursor.execute("SET statement_timeout TO " + ("15000" if schema else "0"))
            cursor.execute(
                f'SET search_path TO "{schema}", pg_catalog'
                if schema
                else "SET search_path TO public"
            )
    finally:
        dbapi_connection.autocommit = prior


_evaluation_shadow = ContextVar("nova_evaluation_shadow", default=False)

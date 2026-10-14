from alembic import context
from sqlalchemy import create_engine

import app.intelligence.models  # noqa: F401 — register Phase 2 metadata for drift checks
import app.model_routing.models  # noqa: F401 — register Phase 4 metadata
import app.perception.models  # noqa: F401 — register Phase 5 metadata
import app.proactive.models  # noqa: F401 — register Phase 3 metadata
from app.config import settings
from app.models import Base

target_metadata = Base.metadata


def run_migrations_offline():
    context.configure(
        url=settings.database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    engine = create_engine(settings.database_url)
    with engine.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()
    engine.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

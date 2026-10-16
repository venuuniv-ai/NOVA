from contextvars import ContextVar
from dataclasses import dataclass
from uuid import UUID

from app.seed import DEMO_USER_ID


@dataclass(frozen=True)
class Principal:
    user_id: UUID
    roles: frozenset[str]
    device_id: UUID | None = None
    mode: str = "demo"


principal = ContextVar("nova_principal", default=None)


def current_user_id():
    value = principal.get()
    # Internal fixtures/CLI retain their explicit demo scope, never request headers.
    return value.user_id if value else DEMO_USER_ID

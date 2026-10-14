from uuid import UUID

from sqlalchemy.dialects.postgresql import insert

from app.database import SessionLocal
from app.models import Device, User

DEMO_USER_ID = UUID("00000000-0000-4000-8000-000000000001")
DEMO_DEVICES = [
    {"id": UUID("00000000-0000-4000-8000-000000000010"), "name": "Desktop", "type": "DESKTOP"},
    {"id": UUID("00000000-0000-4000-8000-000000000020"), "name": "Wearable", "type": "WEARABLE"},
    {"id": UUID("00000000-0000-4000-8000-000000000030"), "name": "Mobile", "type": "MOBILE"},
]


def seed_demo() -> None:
    with SessionLocal.begin() as session:
        session.execute(
            insert(User).values(id=DEMO_USER_ID, name="Demo user").on_conflict_do_nothing()
        )
        for device in DEMO_DEVICES:
            session.execute(
                insert(Device).values(**device, user_id=DEMO_USER_ID).on_conflict_do_nothing()
            )

    from app.memory.service import seed_memories

    seed_memories()


if __name__ == "__main__":
    seed_demo()

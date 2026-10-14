from datetime import UTC, datetime
from typing import Protocol

DEMO_TIME = datetime(2026, 10, 14, 13, 31, tzinfo=UTC)


class Clock(Protocol):
    def now(self) -> datetime: ...


class SystemClock:
    def now(self) -> datetime:
        return datetime.now(UTC)


class FixtureClock:
    def __init__(self, time: datetime = DEMO_TIME):
        if time.tzinfo is None:
            raise ValueError("Clock requires an aware timestamp.")
        self.time = time

    def now(self) -> datetime:
        return self.time

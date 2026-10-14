import hashlib
import json
from datetime import timedelta

from redis import Redis
from redis.exceptions import RedisError

from app.proactive.clock import Clock
from app.proactive.contracts import MeetingContext, Situation


def demo_meeting(clock: Clock, instance: str = "default") -> MeetingContext:
    return MeetingContext(
        meeting_id=f"demo-architecture-review:{instance}",
        title="Architecture Review",
        starts_at=clock.now().replace(hour=14, minute=0, second=0, microsecond=0),
        location="Client Office",
        current_location="Demo home",
        travel_minutes=35,
        confidence=1.0,
        proactive_enabled=True,
    )


class ProactiveTriggerEngine:
    def __init__(self, clock: Clock, threshold: float = 2):
        self.clock = clock
        self.threshold = threshold

    def analyze(self, meeting: MeetingContext) -> tuple[Situation, str]:
        now = self.clock.now()
        available = (meeting.starts_at - now).total_seconds() / 60
        risk = meeting.travel_minutes - available
        situation = Situation(
            meeting=meeting,
            current_time=now,
            minutes_available=available,
            travel_minutes=meeting.travel_minutes,
            lateness_minutes=risk,
            arrival_at=now + timedelta(minutes=meeting.travel_minutes),
        )
        reason = "SURFACE"
        if not meeting.proactive_enabled:
            reason = "PREFERENCE_DISABLED"
        elif available <= 0 or available > 60:
            reason = "OUTSIDE_RELEVANT_WINDOW"
        elif meeting.confidence < 0.8:
            reason = "LOW_CONFIDENCE"
        elif risk <= self.threshold:
            reason = "BELOW_THRESHOLD"
        return situation, reason

    def fingerprint(self, user_id, situation: Situation) -> str:
        stable = {
            "user": str(user_id),
            "meeting": situation.meeting.meeting_id,
            "start": situation.meeting.starts_at.isoformat(),
            "trigger": "MEETING_TRAVEL_RISK",
        }
        return hashlib.sha256(json.dumps(stable, sort_keys=True).encode()).hexdigest()


class RedisCooldown:
    def __init__(self, url: str, prefix: str = "nova:proactive", ttl: int = 300):
        self.client = Redis.from_url(url, socket_connect_timeout=1, socket_timeout=1)
        self.prefix, self.ttl = prefix, ttl

    def claim(self, user_id, fingerprint: str) -> str:
        try:
            accepted = self.client.set(
                f"{self.prefix}:{user_id}:{fingerprint}", "1", nx=True, ex=self.ttl
            )
            return "CLAIMED" if accepted else "COOLDOWN"
        except RedisError:
            return "REDIS_UNAVAILABLE"

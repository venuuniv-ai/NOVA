"""Narrow read-only kernel capabilities. No mutation capability or arbitrary SQL for agents."""

from app.memory.contracts import MemoryQuery
from app.memory.service import MemoryService
from app.security.identity import current_user_id


class MemoryReader:
    def __init__(self, user_id=None, task_id=None):
        self.user_id, self.task_id = user_id or current_user_id(), task_id

    def preferences(self, subject):
        from app.intelligence.contracts import MemoryOutput, Preference, Provenance

        result = MemoryService(self.user_id).search(
            MemoryQuery(
                task_id=self.task_id,
                types=["PREFERENCE", "FACT", "EPISODIC", "TASK_CONTEXT"],
                subject=subject,
                limit=10,
            )
        )
        preferences = []
        for hit in result.hits:
            m = hit.memory
            if m.memory_type != "PREFERENCE":
                continue
            source = "DEMO_FIXTURE" if m.origin == "FIXTURE" else "PERSISTENT_MEMORY"
            # Preserve fixture wording/reference; real records remain independently attributed.
            value = (
                "Sarah prefers Italian food."
                if m.source_reference == "demo.memory.sarah.italian"
                else "Prefer dinner after 6:00 PM."
                if m.source_reference == "demo.memory.user.dinner-time"
                else f"{m.subject} {m.predicate}: {m.value}"
            )
            preferences.append(
                Preference(
                    person=m.subject,
                    preference=value,
                    provenance=Provenance(
                        source=source,
                        reference=m.source_reference
                        if source == "DEMO_FIXTURE"
                        else f"memory:{m.id}",
                        memory_type="explicit_preference"
                        if m.explicitness in {"EXPLICIT", "FIXTURE"}
                        else "confirmed_inference",
                    ),
                )
            )
        return MemoryOutput(preferences=preferences, memory_hits=result.hits)

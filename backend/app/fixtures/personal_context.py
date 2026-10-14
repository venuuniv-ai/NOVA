"""The sole synthetic personal-data source. No real calendar/contact/location access."""

from app.intelligence.contracts import (
    CalendarEvent,
    DeviceContext,
    Evidence,
    LocationContext,
    Preference,
    Provenance,
    SharedContext,
)
from app.schemas import DeviceType


class DemoFixtureRepository:
    source = "DEMO_FIXTURE"

    def calendar(self, date_label: str) -> list[CalendarEvent]:
        if date_label != "tomorrow":
            return []
        return [
            CalendarEvent(
                title="Product Review",
                date_label="tomorrow",
                starts_at="16:00",
                ends_at="17:00",
                location="Downtown",
                provenance=Provenance(reference="demo.calendar.product-review"),
            )
        ]

    def preferences(self, person: str) -> list[Preference]:
        if person.casefold() == "sarah":
            return [
                Preference(
                    person="Sarah",
                    preference="Sarah prefers Italian food.",
                    provenance=Provenance(
                        reference="demo.memory.sarah.italian", memory_type="explicit_preference"
                    ),
                )
            ]
        if person == "demo_user":
            return [
                Preference(
                    person="demo_user",
                    preference="Prefer dinner after 6:00 PM.",
                    provenance=Provenance(
                        reference="demo.memory.user.dinner-time", memory_type="explicit_preference"
                    ),
                )
            ]
        return []

    def device(self, device_type: DeviceType) -> DeviceContext:
        return DeviceContext(
            device_type=device_type, provenance=Provenance(reference="demo.device.context")
        )

    def location(self) -> LocationContext:
        return LocationContext(
            description="Meeting ends near Downtown.",
            area="Downtown",
            provenance=Provenance(reference="demo.location.meeting-end"),
        )


def context_evidence(context: SharedContext) -> list[Evidence]:
    """Project typed plugin context into attributable planning constraints."""
    result = []
    for event in context.calendar:
        result.extend(
            [
                Evidence(
                    fact=f"Meeting ends at {event.ends_at} (5:00 PM).",
                    provenance=event.provenance,
                    plugin="CalendarPlugin",
                    function="find_events_related_to_task",
                ),
                Evidence(
                    fact=f"Meeting is in {event.location}.",
                    provenance=event.provenance,
                    plugin="CalendarPlugin",
                    function="find_events_related_to_task",
                ),
            ]
        )
    for preference in context.preferences:
        result.append(
            Evidence(
                fact=preference.preference,
                provenance=preference.provenance,
                plugin="MemoryPlugin",
                function="get_user_preferences"
                if preference.person == "demo_user"
                else "get_preferences_for_person",
            )
        )
    if context.location:
        result.append(
            Evidence(
                fact=context.location.description,
                provenance=context.location.provenance,
                plugin="ContextPlugin",
                function="get_demo_location_context",
            )
        )
    return result

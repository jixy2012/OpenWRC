"""External API models for WRC data"""

# Event models
from .event_models import (
    EventClass,
    RallyMetadata,
    CountryMetadata,
    EventMetadata,
)

# Entry models
from .entry_models import (
    Person,
    Driver,
    CoDriver,
    Manufacturer,
    Entrant,
    Group,
    Entry,
    RallyEntries,
    StartList,
)

# Result models
from .result_models import (
    ResultEntry,
    RallyResults,
    StageResults,
    StageTimeEntry,
    StageTimeResults,
    ShakedownTimeResults,
)

# Itinerary models
from .itinerary_models import (
    Control,
    Stage,
    ItinerarySection,
    ItineraryLeg,
    Itinerary,
)

__all__ = [
    # Event models
    "EventClass",
    "RallyMetadata",
    "CountryMetadata",
    "EventMetadata",
    # Entry models
    "Person",
    "Driver",
    "CoDriver",
    "Manufacturer",
    "Entrant",
    "Group",
    "Entry",
    "RallyEntries",
    "StartList",
    # Result models
    "ResultEntry",
    "RallyResults",
    "StageResults",
    "StageTimeEntry",
    "StageTimeResults",
    "ShakedownTimeResults",
    # Itinerary models
    "Control",
    "Stage",
    "ItinerarySection",
    "ItineraryLeg",
    "Itinerary",
]

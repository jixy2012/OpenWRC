"""
External API models with Api prefix for clarity.
"""

# Event models
from .event_models import (
    EventMetadata as ApiEventMetadata,
    RallyMetadata as ApiRallyMetadata,
    EventClass as ApiEventClass,
    CountryMetadata as ApiCountry,
)

# Entry models
from .entry_models import (
    Person as ApiPerson,
    Driver as ApiDriver,
    CoDriver as ApiCoDriver,
    Manufacturer as ApiManufacturer,
    Entrant as ApiEntrant,
    Group as ApiGroup,
    Entry as ApiEntry,
    RallyEntries as ApiRallyEntries,
    StartList as ApiStartList,
    StartListItem as ApiStartListItem,
)

# Itinerary models
from .itinerary_models import (
    Itinerary as ApiItinerary,
    ItineraryLeg as ApiItineraryLeg,
    ItinerarySection as ApiItinerarySection,
    Stage as ApiStage,
    Control as ApiControl,
)

# Result models
from .result_models import (
    StageResults as ApiStageResults,
    RallyResults as ApiRallyResults,
    SplitTimeResults as ApiSplitTimeResults,
    StageTimeResults as ApiStageTimeResults,
    ShakedownTimeResults as ApiShakedownTimeResults,
)

__all__ = [
    # Event
    "ApiEventMetadata",
    "ApiRallyMetadata",
    "ApiEventClass",
    "ApiCountry",
    # Entry
    "ApiPerson",
    "ApiDriver",
    "ApiCoDriver",
    "ApiManufacturer",
    "ApiEntrant",
    "ApiGroup",
    "ApiEntry",
    "ApiRallyEntries",
    "ApiStartList",
    "ApiStartListItem",
    # Itinerary
    "ApiItinerary",
    "ApiItineraryLeg",
    "ApiItinerarySection",
    "ApiStage",
    "ApiControl",
    # Results
    "ApiStageResults",
    "ApiRallyResults",
    "ApiSplitTimeResults",
    "ApiStageTimeResults",
    "ApiShakedownTimeResults",
]

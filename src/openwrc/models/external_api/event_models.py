from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from pydantic_extra_types.timezone_name import TimeZoneName


class EventClass(BaseModel):
    # classes like RC1, RC2, etc.
    eventClassId: int
    eventId: int
    name: str = Field(description="Competition class name (e.g., RC1, RC2)")


class RallyMetadata(BaseModel):
    # events can have more than one rally
    rallyId: int = Field(description="Unique identifier for this rally")
    eventId: int

    # each rally has its own itinerary
    itineraryId: int
    name: str
    isMain: bool
    eventClasses: list[EventClass]


class CountryMetadata(BaseModel):
    countryId: int
    name: str
    iso2: str = Field(min_length=2, max_length=2)
    iso3: str = Field(min_length=3, max_length=3)


class EventMetadata(BaseModel):

    # default to allowing extra fields from external sources
    model_config = ConfigDict(extra="ignore")

    rallies: list[RallyMetadata]
    eventClasses: list[EventClass] = Field(
        description="All competition classes in this event"
    )
    eventId: int

    countryId: int
    country: CountryMetadata
    name: str = Field(description="Official event name")

    slug: str = Field(description="uri slug maybe useful for some requests")
    location: str
    startDate: datetime
    finishDate: datetime
    timeZoneId: TimeZoneName = Field(
        description="IANA timezone identifier for event location"
    )
    timeZoneName: str

    surfaces: str  # TODO: enum it

    shakedownCount: int = Field(description="Number of shakedown stages")

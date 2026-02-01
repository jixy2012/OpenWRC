from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from pydantic import ConfigDict, Field, model_validator
from pydantic_extra_types.timezone_name import TimeZoneName
from .base_external_model import WrcExternalApiBaseModel


class EventClass(WrcExternalApiBaseModel):
    # classes like RC1, RC2, etc.
    event_class_id: int
    event_id: int
    name: str = Field(description="Competition class name (e.g., RC1, RC2)")


class RallyMetadata(WrcExternalApiBaseModel):
    # events can have more than one rally
    rally_id: int = Field(description="Unique identifier for this rally")
    event_id: int

    # each rally has its own itinerary
    itinerary_id: int
    name: str
    is_main: bool
    event_classes: list[EventClass]


class CountryMetadata(WrcExternalApiBaseModel):
    country_id: int
    name: str
    iso2: str = Field(min_length=2, max_length=2)
    iso3: str = Field(min_length=3, max_length=3)


def convert_to_utc(dt: datetime, tz: TimeZoneName) -> datetime:
    """
    the base model will always try to convert all times to utc.
    when a time is specified to be a local time, use this util to convert to utc
    """
    if dt.tzinfo and dt.tzinfo == timezone.utc:
        native = dt.replace(tzinfo=None)
        # Convert timezone name string to ZoneInfo object
        event_tz = ZoneInfo(str(tz))
        local = native.replace(tzinfo=event_tz)
        return local.astimezone(timezone.utc)
    return dt


class EventMetadata(WrcExternalApiBaseModel):

    # default to allowing extra fields from external sources
    model_config = ConfigDict(extra="ignore")

    rallies: list[RallyMetadata] = Field(min_length=1)
    event_classes: list[EventClass] = Field(
        description="All competition classes in this event"
    )
    event_id: int

    country_id: int
    country: CountryMetadata
    name: str = Field(description="Official event name")

    slug: str = Field(description="uri slug maybe useful for some requests")
    location: str
    start_date: datetime
    finish_date: datetime
    time_zone_id: TimeZoneName = Field(
        description="IANA timezone identifier for event location"
    )
    time_zone_name: str

    surfaces: str  # TODO: enum it

    shakedown_count: int = Field(description="Number of shakedown stages")

    @model_validator(mode="after")
    def convert_start_finish_to_utc(self) -> "EventMetadata":
        """we convert start and finish dates from local time to utc time for easier comparison"""
        self.start_date = convert_to_utc(self.start_date, self.time_zone_id)
        self.finish_date = convert_to_utc(self.finish_date, self.time_zone_id)
        return self

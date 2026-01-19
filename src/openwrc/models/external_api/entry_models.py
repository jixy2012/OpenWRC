"""Models for rally entries (drivers, codrivers, cars) from WRC API"""

from typing import Optional
from pydantic import Field, ConfigDict

from .base_external_model import WrcExternalApiBaseModel
from .event_models import CountryMetadata, EventClass


class Person(WrcExternalApiBaseModel):
    """Base model for driver or codriver"""

    model_config = ConfigDict(extra="ignore")

    personId: int = Field(description="Unique identifier for this person")
    countryId: int
    country: CountryMetadata

    seasonId: Optional[int] = Field(default=None)
    eventId: Optional[int] = Field(default=None)
    externalId: Optional[str] = Field(default=None)

    # Name fields
    firstName: str
    lastName: str
    abbvName: str = Field(description="Abbreviated name (e.g., S. OGIER)")
    fullName: str = Field(description="Full display name")
    code: str = Field(description="Three-letter code (e.g., OGI)")

    licenseNumber: Optional[str] = Field(default=None)
    state: Optional[str] = Field(default="")


class Driver(Person):
    """Driver information"""

    pass


class CoDriver(Person):
    """Co-driver information"""

    pass


class Manufacturer(WrcExternalApiBaseModel):
    """Manufacturer/car brand information"""

    manufacturerId: int = Field(description="Unique identifier for manufacturer")
    name: str = Field(description="Manufacturer name (e.g., Toyota, Hyundai)")
    logoFilename: Optional[str] = Field(
        default=None, description="Logo filename reference"
    )


class Entrant(WrcExternalApiBaseModel):
    """Team/entrant information"""

    entrantId: int = Field(description="Unique identifier for the team")
    name: str = Field(description="Team name (e.g., TOYOTA GAZOO RACING WRT)")
    logoFilename: Optional[str] = Field(
        default=None, description="Logo filename reference"
    )


class Group(WrcExternalApiBaseModel):
    """Competition group (Rally1, Rally2, etc.)"""

    groupId: int = Field(description="Unique identifier for this group")
    name: str = Field(description="Group name (e.g., Rally1, Rally2)")


class Entry(WrcExternalApiBaseModel):
    """
    Complete entry for a driver/car/team combination in an event.
    This is the main unit that competes in rallies.
    """

    model_config = ConfigDict(extra="ignore")

    # Main identifiers
    entryId: int = Field(description="Unique identifier for this entry")
    eventId: int

    # Related entities
    driver: Driver
    codriver: CoDriver
    manufacturer: Manufacturer
    entrant: Entrant
    group: Group
    eventClasses: list[EventClass]

    # IDs for relationships
    driverId: int
    codriverId: int
    manufacturerId: int
    entrantId: int
    groupId: int

    # Entry details
    identifier: str = Field(description="Car number as string")
    vehicleModel: str = Field(description="Specific car model (e.g., GR Yaris Rally1)")
    entryListOrder: int = Field(description="Order in entry list")

    # Competition details
    eligibility: str = Field(description="Eligibility code (e.g., M for Manufacturer)")
    priority: str = Field(description="Priority classification (e.g., P1)")
    status: str = Field(description="Entry status (e.g., Entry, Retired)")
    tyreManufacturer: str = Field(
        description="Tyre manufacturer name, seems to not be populated from api"
    )

    # Optional fields
    pbf: Optional[str] = Field(default=None)
    drive: Optional[str] = Field(default=None)
    tags: list[str] = Field(default_factory=list)


# Type alias for list of entries
RallyEntries = list[Entry]

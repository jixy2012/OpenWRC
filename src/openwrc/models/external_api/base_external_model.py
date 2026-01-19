from datetime import datetime, timezone
from pydantic import BaseModel, model_validator, ConfigDict


class WrcExternalApiBaseModel(BaseModel):
    model_config = ConfigDict(extra="ignore")

    @model_validator(mode="after")
    def make_datetime_timezone_explicit(self) -> "WrcExternalApiBaseModel":
        for field_name, field_value in self.__dict__.items():
            if isinstance(field_value, datetime) and not field_value.tzinfo:
                setattr(self, field_name, field_value.replace(tzinfo=timezone.utc))
        return self

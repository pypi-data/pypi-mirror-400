import os
from pydantic import BaseModel, model_validator, field_validator
from typing import Optional, Any


# https://docs.pydantic.dev/latest/migration/#required-optional-and-nullable-fields
class Altinn3CloudEvent(BaseModel):
    alternativesubject: Optional[str] = None
    data: Optional[Any] = None
    datacontenttype: Optional[str] = None
    id: str
    source: str
    specversion: str
    subject: Optional[str] = None
    time: Optional[str] = None
    type: str
    resource: Optional[str] = None
    resourceinstance: Optional[str] = None

    @field_validator("source")
    def validate_event_source(cls, v: str) -> str:
        expected: str = os.getenv("APPROVED_EVENT_SOURCE_URL")
        if not expected:
            raise ValueError(
                "Environment variable 'APPROVED_EVENT_SOURCE_URL' not found!"
            )
        options = expected.split(",")

        for option in options:
            if v.startswith(option):
                return v
        raise ValueError(
            f"Provided event source '{v}' did not match expected source '{expected}'"
        )

    @model_validator(mode="before")
    def validate_optionals(cls, values):
        t = values.get("type")
        if t == "platform.events.validatesubscription":
            return values

        if not values.get("time"):
            raise ValueError(
                "Field 'time' must have a value for all non-validation events."
            )

        if not values.get("subject"):
            raise ValueError(
                "Field 'subject' must have a value for all non-validation events."
            )

        return values

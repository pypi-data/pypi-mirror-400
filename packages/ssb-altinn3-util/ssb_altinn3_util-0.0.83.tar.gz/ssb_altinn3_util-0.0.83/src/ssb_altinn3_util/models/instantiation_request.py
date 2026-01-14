from datetime import datetime
from pydantic import BaseModel
from typing import Dict, Optional
from defusedxml import ElementTree as ET


class InstantiationMetadata(BaseModel):
    edition: int
    raNumber: str
    batch_ref: str


class InstanceOwner(BaseModel):
    personNumber: Optional[str] = None
    organisationNumber: Optional[str] = None


class InstanceContent(BaseModel):
    dueBefore: datetime
    visibleAfter: datetime
    instanceOwner: InstanceOwner
    dataValues: Dict[str, str]


class InstantiationRequestModel(BaseModel):
    metadata: InstantiationMetadata
    instanceContent: InstanceContent
    dataModel: Optional[str] = None
    prefillContent: str

    def get_schema_and_survey_number(self) -> str:
        """Returns the ra-number and survey number. To be used for
        schemas which needs to be authorized on schema and survey number"""

        xml_root = ET.fromstring(self.prefillContent)
        survey_number = xml_root.find(".//undersoekelsesNr")
        return f"{self.metadata.raNumber}-{survey_number.text}"

    def get_identyfying_fields(self) -> list:
        return self.instanceContent.dataValues["identifyingFields"].split(",")

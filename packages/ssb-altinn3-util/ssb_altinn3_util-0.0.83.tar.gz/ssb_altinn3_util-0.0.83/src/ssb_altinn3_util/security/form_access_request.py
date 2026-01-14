from typing import Optional
from pydantic import field_validator, BaseModel, ValidationError


class FormAccessRequest(BaseModel):
    """
    Request model used when requesting a change in form access privileges for a group.
    Possible access type are "r" (read), "w" (write) and None (remove access to form).
    """

    group_name: str
    ra_number: str
    survey_number: int
    access_type: Optional[str] = None
    performed_by: str

    @field_validator("access_type")
    @classmethod
    def valid_access_type(cls, v):
        if v and v not in ["r", "w"]:
            raise ValueError(
                "Access type must be either 'r' (read), 'w' (write) or None (revoke access)."
            )
        return v

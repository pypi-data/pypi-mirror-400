from pydantic import field_validator, BaseModel, ValidationError


class PostFormRequest(BaseModel):
    ra_number: str
    survey_number: int


class PostGroupRequest(BaseModel):
    group_name: str


class PostGroupFormAccess(BaseModel):
    form_id: int
    group_id: int
    access_type: str
    user: str

    @field_validator("access_type")
    @classmethod
    def valid_access_type(cls, v):
        if v not in ["r", "w"]:
            raise ValueError("Access type must be either 'r' (read), 'w' (write).")
        return v


class PostGroupRoleAccess(BaseModel):
    role_id: int
    group_id: int
    user: str

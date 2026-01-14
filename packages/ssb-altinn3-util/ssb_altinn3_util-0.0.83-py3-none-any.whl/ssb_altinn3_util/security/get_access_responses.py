from datetime import datetime
from pydantic import BaseModel
from typing import List, Optional


class Form(BaseModel):
    id: int
    ra_number: str
    survey_number: int


class Group(BaseModel):
    id: int
    group_name: str


class Role(BaseModel):
    id: int
    role_name: str


class GetFormWithGroupsResponse(BaseModel):
    form: Form
    readers: List[Group]
    writers: List[Group]


class GetGroupWithRolesAndFormsResponse(BaseModel):
    group: Group
    direct_roles: List[Role]
    inherited_roles: List[Role]
    forms_read: List[Form]
    forms_write: List[Form]


class GetRoleWithGroupsResponse(BaseModel):
    role: Role
    direct_members: List[Group]
    inherited_members: List[Group]


class GroupFormAccessResponse(BaseModel):
    form_id: int
    group_id: int
    ra_number: str
    survey_number: int
    access_type: str
    granted_by: str
    granted_at: datetime
    last_changed_by: Optional[str] = None
    last_changed_at: Optional[datetime] = None

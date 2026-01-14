from typing import Optional
from pydantic import BaseModel


class AuthorizationRequest(BaseModel):
    user_email: str
    requested_role: str
    form_access_key: Optional[str] = None
    is_root_element: Optional[bool] = None

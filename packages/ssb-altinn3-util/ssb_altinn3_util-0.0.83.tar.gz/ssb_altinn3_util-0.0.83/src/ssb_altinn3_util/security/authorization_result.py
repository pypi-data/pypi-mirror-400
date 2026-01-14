from pydantic import BaseModel
from typing import List, Optional


class AuthorizationResult(BaseModel):
    access_granted: bool
    status_code: int
    error_message: Optional[str] = None
    allowed_forms_read: List[str]
    allowed_forms_write: List[str]

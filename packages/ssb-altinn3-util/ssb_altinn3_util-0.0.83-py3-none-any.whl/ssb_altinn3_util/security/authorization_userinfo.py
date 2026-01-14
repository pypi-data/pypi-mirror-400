from pydantic import BaseModel
from typing import List


class UserInfoResult(BaseModel):
    name: str
    email: str
    status_code: int
    roles: List[str]
    forms: List[str]

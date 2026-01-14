from typing import Generic, List, TypeVar
from pydantic import Field, BaseModel
from typing_extensions import Annotated


class PageParams(BaseModel):
    page: Annotated[int, Field(ge=1)] = 1
    size: Annotated[int, Field(ge=1, le=100)] = 10
    order_by: str = ""
    asc: bool = True


T = TypeVar("T")


class PagedResponse(BaseModel, Generic[T]):
    total: int
    page: int
    size: int
    results: List[T]

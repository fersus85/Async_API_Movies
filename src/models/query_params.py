from typing import Optional

from pydantic import BaseModel, Field


class QueryParams(BaseModel):
    query: Optional[str] = Field(None, description="Search query string")
    page_size: int = Field(..., gt=0, description="Number of items per page")
    page_number: int = Field(..., gt=0, description="Current page number")


class SortableQueryParams(QueryParams):
    sort: str = Field(
        ...,
        description="Field to sort by,"
        " prefix with '-' for descending order",
    )

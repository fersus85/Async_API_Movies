from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class GenreBase(BaseModel):
    """
    GenreBase is used to link genre entities with films in the Film model.
    """

    id: UUID
    name: str


class Genre(GenreBase):
    description: Optional[str] = None

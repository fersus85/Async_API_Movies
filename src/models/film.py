from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel

from models.genre import GenreBase
from models.person import PersonBase


class Film(BaseModel):
    id: UUID
    title: str
    description: Optional[str] = None
    creation_date: Optional[datetime] = None
    imdb_rating: Optional[float] = None
    directors: List[PersonBase]
    actors: List[PersonBase]
    writers: List[PersonBase]
    genres: List[GenreBase]


class FilmShort(BaseModel):
    uuid: UUID
    title: str
    imdb_rating: Optional[float] = None

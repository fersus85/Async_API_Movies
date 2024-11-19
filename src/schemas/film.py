from uuid import UUID
from typing import Optional, List

from pydantic import BaseModel


class UUIDMixin(BaseModel):
    uuid: UUID


class FilmPerson(UUIDMixin):
    full_name: str


class GenreFilm(UUIDMixin):
    name: str


class FilmSchema(UUIDMixin):
    title: str
    imdb_rating: Optional[float]


class FilmDetailSchema(FilmSchema):
    description: Optional[str]
    genre: List[GenreFilm]
    actors: List[FilmPerson]
    writers: List[FilmPerson]
    directors: List[FilmPerson]

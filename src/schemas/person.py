from uuid import UUID
from typing import List, Literal
from pydantic import BaseModel


PERSON_ROLES = Literal['actor', 'director', 'writer']


class UUIDMixin(BaseModel):
    uuid: UUID


class PersonFilmSchema(UUIDMixin):
    roles: List[PERSON_ROLES]


class PersonSchema(UUIDMixin):
    full_name: str
    films: List[PersonFilmSchema]


class FilmByPersonSchema(UUIDMixin):
    title: str
    imdb_rating: float

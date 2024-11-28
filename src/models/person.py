from typing import Literal, List
from uuid import UUID

from pydantic import BaseModel

PERSON_ROLES = Literal["actor", "director", "writer"]


class PersonFilm(BaseModel):
    uuid: UUID
    roles: List[PERSON_ROLES]


class PersonBase(BaseModel):
    """
    PersonBase is used to link person entities with films in the Film model.
    """

    id: UUID
    full_name: str


class Person(PersonBase):
    films: List[PersonFilm]

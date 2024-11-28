from uuid import UUID
from typing import List, Literal, Optional
from pydantic import BaseModel, Field


PERSON_ROLES = Literal["actor", "director", "writer"]


class UUIDMixin(BaseModel):
    uuid: UUID = Field(
        ...,
        title="Уникальный идентификатор",
        examples=["123e4567-e89b-12d3-a456-426614174000"],
    )


class PersonFilmSchema(UUIDMixin):
    roles: List[PERSON_ROLES] = Field(..., description="Список с ролями")


class PersonSchema(UUIDMixin):
    full_name: str = Field(
        ..., title="Полное имя персоны", examples=["Оскар Уайлд"]
    )
    films: List[PersonFilmSchema] = Field(..., description="Список с ролями")


class FilmByPersonSchema(UUIDMixin):
    title: str = Field(..., title="Название фильма", examples=["Pulp Fiction"])
    imdb_rating: Optional[float] = Field(default=None, title="Рейтинг фильма")

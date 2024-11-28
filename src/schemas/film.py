from uuid import UUID
from typing import Optional, List

from pydantic import BaseModel, Field


class UUIDMixin(BaseModel):
    uuid: UUID = Field(
        ...,
        title="Уникальный идентификатор",
        examples=["123e4567-e89b-12d3-a456-426614174000"],
    )


class FilmPerson(UUIDMixin):
    full_name: str = Field(
        ..., title="Полное имя персоны", examples=["Оскар Уайлд"]
    )


class GenreFilm(UUIDMixin):
    name: str = Field(..., title="Название жанра", examples=["Action"])


class FilmSchema(UUIDMixin):
    title: str = Field(..., title="Название фильма", examples=["Pulp Fiction"])
    imdb_rating: Optional[float] = Field(default=None, title="Рейтинг фильма")


class FilmDetailSchema(FilmSchema):
    description: Optional[str] = Field(default=None, title="Описание фильма")
    genre: List[GenreFilm] = Field(
        ..., description="Список жанров, к которым относится фильм"
    )
    actors: List[FilmPerson] = Field(
        ..., description="Список актеров, снимавшихся в фильме"
    )
    writers: List[FilmPerson] = Field(
        ..., description="Список сценаристов фильма"
    )
    directors: List[FilmPerson] = Field(
        ..., description="Список режиссеров фильма"
    )

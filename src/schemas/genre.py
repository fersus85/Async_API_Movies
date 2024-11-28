from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class UUIDMixin(BaseModel):
    uuid: UUID = Field(
        ...,
        title="Уникальный идентификатор",
        examples=["123e4567-e89b-12d3-a456-426614174000"],
    )


class GenreSchema(UUIDMixin):
    name: str = Field(..., description="Название жанра", examples=["Action"])
    description: Optional[str] = Field(
        default=None, description="Описание жанра"
    )

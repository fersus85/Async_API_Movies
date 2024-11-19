from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class UUIDMixin(BaseModel):
    uuid: UUID


class GenreSchema(UUIDMixin):
    name: str
    description: Optional[str]

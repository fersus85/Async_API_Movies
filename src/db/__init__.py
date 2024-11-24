import abc
from typing import Optional, Any, List, Dict

from pydantic import BaseModel, Field


class QueryParams(BaseModel):
    query: Optional[str] = Field(None,
                                 description="Search query string")
    page_size: int = Field(..., gt=0,
                           description="Number of items per page")
    page_number: int = Field(..., gt=0,
                             description="Current page number")


class SortableQueryParams(QueryParams):
    sort: str = Field(...,
                      description="Field to sort by,"
                                  " prefix with '-' for descending order")


class IQuery(abc.ABC):
    @abc.abstractmethod
    def __init__(self, params: QueryParams):
        self.query = None


class ISearchEngine(abc.ABC):
    """
    Abstract base class for search functionality.

    Args:
        client: The search client.
    """

    @abc.abstractmethod
    def __init__(self, client: Any):
        pass

    @abc.abstractmethod
    async def get(self, data_source: str, id: str) -> Optional[Dict[str, Any]]:
        pass

    @abc.abstractmethod
    async def search(self,
                     data_source: str,
                     search_query: IQuery) -> List[Dict[str, Any]]:
        pass

    @abc.abstractmethod
    async def count(self, data_source: str) -> int:
        pass


search_engine: Optional[ISearchEngine] = None


# Функция понадобится при внедрении зависимостей
async def get_search_engine() -> ISearchEngine:
    return search_engine

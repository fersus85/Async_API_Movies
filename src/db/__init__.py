from abc import ABC, abstractmethod
from typing import Optional, Any, List, Dict, Type

from pydantic import BaseModel, Field

from utils.utils import get_all_subclasses


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


class IQuery(ABC):
    @abstractmethod
    def __init__(self, params: QueryParams):
        pass

    @classmethod
    @abstractmethod
    def linked_searcher_class(cls) -> Type:
        pass


class IElasticQuery(IQuery):
    @abstractmethod
    def __init__(self, params: QueryParams):
        pass

    @classmethod
    def linked_searcher_class(self):
        import db.elastic as elastic
        return elastic.ElasticSearchEngine

    @staticmethod
    def _get_offset(page_number: int, page_size: int) -> int:
        return (page_number - 1) * page_size


class FilmQuery(IQuery, ABC):
    pass


class ElasticFilmQuery(IElasticQuery, FilmQuery):
    def __init__(self, params: QueryParams):
        offset = self._get_offset(params.page_number, params.page_size)
        self.query = {
            "query": {
                "multi_match": {
                    "query": params.query,
                    "fields": ["title", "directors", "actors", "writers"],
                    "type": "best_fields",
                }
            },
            "from": offset,
            "size": params.page_size,
        }


class PopularFilmQuery(IQuery, ABC):
    pass


class ElasticPopularFilmQuery(IElasticQuery, PopularFilmQuery):
    def __init__(self, params: QueryParams):
        if not hasattr(params, "sort"):
            raise ValueError("ElasticPopularFilmQuery only"
                             " supports params with sort attribute")

        offset = self._get_offset(params.page_number, params.page_size)
        order = "desc" if params.sort.startswith("-") else "asc"
        sort_field = params.sort.lstrip("-")

        self.query = {
            "query": {"bool": {"must": [{"match_all": {}}]}},
            "sort": [{sort_field: {"order": order}}],
            "from": offset,
            "size": params.page_size,
        }

        if params.query:
            self.query["query"]["bool"]["filter"] = [
                {
                    "nested": {
                        "path": "genres",
                        "query": {"term": {"genres.id": params.query}},
                    }
                }
            ]


class GenreQuery(IQuery, ABC):
    pass


class ElasticGenreQuery(IElasticQuery, GenreQuery):
    def __init__(self, params: QueryParams):
        offset = self._get_offset(params.page_number, params.page_size)

        self.query = {
            "query": {"match_all": {}},
            "from": offset,
            "size": params.page_size
        }


class PersonQuery(IQuery, ABC):
    pass


class ElasticPersonQuery(IElasticQuery, PersonQuery):
    def __init__(self, params: QueryParams):
        offset = self._get_offset(params.page_number, params.page_size)

        self.query = {
            "query": {"match": {"full_name": params.query}},
            "from": offset,
            "size": params.page_size,
        }


class FilmsByPersonIDQuery(IQuery, ABC):
    pass


class ElasticFilmsByPersonIDQuery(IElasticQuery, FilmsByPersonIDQuery):
    def __init__(self, params: QueryParams):
        offset = self._get_offset(params.page_number, params.page_size)

        self.query = {
            "query": {
                "bool": {
                    "should": [
                        {
                            "nested": {
                                "path": "actors",
                                "query":
                                    {"term": {"actors.id": params.query}},
                            }
                        },
                        {
                            "nested": {
                                "path": "writers",
                                "query":
                                    {"term": {"writers.id": params.query}},
                            }
                        },
                        {
                            "nested": {
                                "path": "directors",
                                "query":
                                    {"term": {"directors.id": params.query}},
                            }
                        },
                    ]
                }
            },
            "from": offset,
            "size": params.page_size,
        }


class ISearchEngine(ABC):
    """
    Abstract base class for search functionality.

    Args:
        client: The search client.
    """

    @abstractmethod
    def __init__(self, client: Any):
        pass

    @abstractmethod
    async def get(self, data_source: str, id: str) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    async def search(self,
                     data_source: str,
                     search_query: IQuery) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    async def count(self, data_source: str) -> int:
        pass


def query_factory(search_engine_: Type[ISearchEngine] | ISearchEngine,
                  query_cls: Type[IQuery],
                  params: QueryParams) -> IQuery:
    if isinstance(search_engine_, ISearchEngine):
        search_engine_cls = type(search_engine_)

    query_classes = get_all_subclasses(query_cls)
    linked_query = [cls for cls in query_classes
                    if cls.linked_searcher_class() == search_engine_cls]

    if len(linked_query) > 1:
        raise ValueError("Multiple query classes found for "
                         f"{search_engine_cls.__name__} in "
                         f"{query_cls.__name__}")
    elif len(linked_query) == 0:
        raise ValueError(f"No query class found for "
                         f"{search_engine_cls.__name__} in "
                         f"{query_cls.__name__}")

    return linked_query[0](params)


search_engine: Optional[ISearchEngine] = None


# Функция понадобится при внедрении зависимостей
async def get_search_engine() -> ISearchEngine:
    return search_engine

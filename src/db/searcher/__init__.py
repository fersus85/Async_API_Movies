from abc import ABC, abstractmethod
from typing import Optional, Any, List, Dict, Type, Union

from models.query_params import QueryParams
from utils.utils import get_all_subclasses


class IQuery(ABC):
    @abstractmethod
    def __init__(self, params: QueryParams):
        pass

    @classmethod
    @abstractmethod
    def linked_searcher_class(cls) -> Type:
        pass


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


def query_factory(search_engine_: Union[Type[ISearchEngine], ISearchEngine],
                  query_cls: Type[IQuery],
                  params: QueryParams) -> IQuery:
    if isinstance(search_engine_, ISearchEngine):
        search_engine_cls = type(search_engine_)
    else:
        search_engine_cls = search_engine_

    query_classes = get_all_subclasses(query_cls)
    linked_query = [cls for cls in query_classes
                    if cls.linked_searcher_class == search_engine_cls]

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


# пока подразумевается, что search_engine всего один
async def get_search_engine() -> ISearchEngine:
    return search_engine

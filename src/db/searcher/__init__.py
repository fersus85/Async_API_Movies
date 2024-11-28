from abc import ABC, abstractmethod
from typing import Optional, Any, List, Dict, Type, Union

from models.query_params import QueryParams
from utils.utils import get_all_subclasses


class IQuery(ABC):
    """
    Abstract Base Class for query objects.

    Example structure:
       +------------------+
       |     IQuery       |<----------------+
       |------------------|                 |
       | + linked_searcher|                 |
       |   _class: Type   |                 |
       | + __init__()     |                 |
       |------------------|                 |
                ^                           |
                |                           |
   +---------------------+          +------------------+
   |   IElasticQuery     |          |    FilmQuery     |
   |---------------------|          |------------------|
   | + linked_searcher   |          |                  |
   |   _class:           |          |                  |
   |   ElasticSearchEngine|         |                  |
   | + __init__()         |         |                  |
   | + _get_offset()      |         |                  |
   +---------------------+          +------------------+
                ^                           ^
                |                           |
                +-----------+---------------+
                            |
            +-----------------------------+
            |     ElasticFilmQuery        |
            |-----------------------------|
            | + __init__(params)          |
            | + query: dict               |
            |-----------------------------|
    """
    @abstractmethod
    def __init__(self, params: QueryParams):
        """
        Initialize the query with the given parameters.
        """
        pass

    @property
    @classmethod
    @abstractmethod
    def linked_searcher_class(cls) -> Type:
        """
        The search engine class associated with this query.
        """
        pass


class ISearchEngine(ABC):
    """
    An abstract base class that defines the interface for a search engine.
    """

    @abstractmethod
    def __init__(self, client: Any):
        """
        Initializes the search engine instance.

        Args:
            client (Any): The client object used for communication with
                          the underlying data source or search backend.

        This method should set up the required configurations or
        connections for the search engine implementation.
        """
        pass

    @abstractmethod
    async def get(self, data_source: str, id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves a single document by its unique identifier.

        Args:
            data_source (str): The name or identifier of the data source.
            id (str): The unique identifier of the document to retrieve.

        Returns:
            Optional[Dict[str, Any]]: The retrieved document as a dictionary,
                                      or None if the document is not found.

        This method should query the specified data source and return the
        document that matches the given ID.
        """
        pass

    @abstractmethod
    async def search(self,
                     data_source: str,
                     search_query: IQuery) -> List[Dict[str, Any]]:
        """
        Performs a search query on the specified data source.

        Args:
            data_source (str): The name or identifier of the data source.
            search_query (IQuery): An object representing the search query.

        Returns:
            List[Dict[str, Any]]: The retrieved document
                                  as a list of dictionaries.

        This method should process the search query and return all results
        that match the specified criteria.
        """
        pass

    @abstractmethod
    async def count(self, data_source: str) -> int:
        """
        Counts the total number of documents in the specified data source.

        Args:
            data_source (str): The name or identifier of the data source.

        Returns:
            int: The total number of documents available in the data source.

        This method should query the data source and return the count of all
        documents it contains.
        """
        pass


def query_factory(search_engine_: Union[Type[ISearchEngine], ISearchEngine],
                  query_cls: Type[IQuery],
                  params: QueryParams) -> IQuery:
    """
    Factory function to create an instance of a query associated
    with the specified search engine.

    Arguments:
        search_engine_ (Union[Type[ISearchEngine], ISearchEngine]):
                The class or instance of the search engine.

        query_cls (Type[IQuery]):
                The base query class, which is extended
                by specific implementations.

        params (QueryParams):
                Parameters to initialize the query instance.

    Returns:
        IQuery: An instance of the query class associated
                with the specified search engine.
    """
    search_engine_cls = type(search_engine_) if not (
        isinstance(search_engine_, ISearchEngine)) else search_engine_

    query_classes = get_all_subclasses(query_cls)

    linked_query = [
        cls for cls in query_classes
        if cls.linked_searcher_class == search_engine_cls
    ]

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

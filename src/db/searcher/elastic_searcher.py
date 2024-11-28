from __future__ import annotations

import logging
from abc import abstractmethod
from typing import Any, Optional, Dict, List

from elasticsearch import NotFoundError, AsyncElasticsearch

from db.searcher import ISearchEngine
from db.searcher.query import IQuery, FilmQuery, PopularFilmQuery, \
    GenreQuery, PersonQuery, FilmsByPersonIDQuery
from models.query_params import QueryParams

logger = logging.getLogger(__name__)


class ElasticSearchEngine(ISearchEngine):
    """
    ElasticSearchEngine is an implementation of the ISearchEngine interface,
    designed to interact with an Elasticsearch cluster using
    an AsyncElasticsearch client.
    """
    def __init__(self, client: Any):
        """
        Initializes the ElasticSearchEngine with an AsyncElasticsearch client.
        """
        if not isinstance(client, AsyncElasticsearch):
            raise TypeError("ElasticSearch client must"
                            " be an AsyncElasticsearch instance")

        self.client = client

    async def get(self, data_source: str, id: str) -> Optional[Dict[str, Any]]:
        """
        Asynchronously retrieves a document from a
        specified Elasticsearch index by its ID.
        """
        logger.debug("get_by_id: %s", id)

        try:
            response = await self.client.get(index=data_source, id=id)
            return response["_source"]
        except NotFoundError:
            return None

    async def search(self,
                     data_source: str,
                     search_query: IElasticQuery) -> List[Dict[str, Any]]:
        """
        Executes a search query against a specified Elasticsearch
        index using an instance of IElasticQuery.
        """
        query = search_query.query

        if not isinstance(search_query, IElasticQuery):
            raise TypeError("search_query must be instance of IElasticQuery")

        try:
            logger.debug("query: %s", query)
            response = await self.client.search(index=data_source, body=query)
            logger.debug("Validating response from ES")

            return [hit["_source"] for hit in response["hits"]["hits"]]
        except NotFoundError:
            return []

    async def count(self, data_source: str) -> int:
        """
        Asynchronously counts the number
        of documents in a specified Elasticsearch index.
        """
        resp = await self.client.count(index=data_source)
        return resp["count"]


class IElasticQuery(IQuery):
    linked_searcher_class = ElasticSearchEngine

    @abstractmethod
    def __init__(self, params: QueryParams):
        pass

    @staticmethod
    def _get_offset(page_number: int, page_size: int) -> int:
        return (page_number - 1) * page_size


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


class ElasticGenreQuery(IElasticQuery, GenreQuery):
    def __init__(self, params: QueryParams):
        offset = self._get_offset(params.page_number, params.page_size)

        self.query = {
            "query": {"match_all": {}},
            "from": offset,
            "size": params.page_size
        }


class ElasticPersonQuery(IElasticQuery, PersonQuery):
    def __init__(self, params: QueryParams):
        offset = self._get_offset(params.page_number, params.page_size)

        self.query = {
            "query": {"match": {"full_name": params.query}},
            "from": offset,
            "size": params.page_size,
        }


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

import abc
import logging
from typing import Optional, Any, List

from elasticsearch import AsyncElasticsearch, NotFoundError
from pydantic import BaseModel

from db import IQuery, QueryParams, ISearchEngine

logger = logging.getLogger(__name__)


class IElasticQuery(IQuery):
    @abc.abstractmethod
    def __init__(self, params: QueryParams):
        self.query = None

    @staticmethod
    def _get_offset(page_number: int, page_size: int) -> int:
        return (page_number - 1) * page_size


class ElasticFilmQuery(IElasticQuery):
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


class ElasticPopularFilmQuery(IElasticQuery):
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


class ElasticGenreQuery(IElasticQuery):
    def __init__(self, params: QueryParams):
        offset = self._get_offset(params.page_number, params.page_size)

        self.query = {
            "query": {"match_all": {}},
            "from": offset,
            "size": params.page_size
        }


class ElasticPersonQuery(IElasticQuery):
    def __init__(self, params: QueryParams):
        offset = self._get_offset(params.page_number, params.page_size)

        self.query = {
            "query": {"match": {"full_name": params.query}},
            "from": offset,
            "size": params.page_size,
        }


class ElasticFilmsByPersonIDQuery(IElasticQuery):
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


class ElasticSearchEngine(ISearchEngine):
    def __init__(self, client: Any):
        if not isinstance(client, AsyncElasticsearch):
            raise TypeError("ElasticSearch client must"
                            " be an AsyncElasticsearch instance")

        self.client = client

    async def get(self, data_source: str, id: str) -> Optional[BaseModel]:
        logger.debug("get_by_id: %s", id)

        try:
            response = await self.client.get(index=data_source, id=id)
            return response["_source"]
        except NotFoundError:
            return None

    async def search(self,
                     data_source: str,
                     search_query: IElasticQuery) -> List[BaseModel]:
        query = search_query.query

        try:
            logger.debug("query: %s", query)
            response = await self.client.search(index=data_source, body=query)
            logger.debug("Validating response from ES")

            return [hit["_source"] for hit in response["hits"]["hits"]]
        except NotFoundError:
            return []

    async def count(self, data_source: str) -> int:
        resp = await self.client.count(index=data_source)
        return resp["count"]


es_client: Optional[AsyncElasticsearch] = None


# Функция понадобится при внедрении зависимостей
async def get_elastic_client() -> AsyncElasticsearch:
    return es_client

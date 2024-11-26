import logging
from typing import Optional, Any, List, Dict

from elasticsearch import AsyncElasticsearch, NotFoundError
from pydantic import BaseModel

from db import ISearchEngine, IElasticQuery, IQuery

logger = logging.getLogger(__name__)


class ElasticSearchEngine(ISearchEngine):
    def __init__(self, client: Any):
        if not isinstance(client, AsyncElasticsearch):
            raise TypeError("ElasticSearch client must"
                            " be an AsyncElasticsearch instance")

        self.client = client

    async def get(self, data_source: str, id: str) -> Optional[Dict[str, Any]]:
        logger.debug("get_by_id: %s", id)

        try:
            response = await self.client.get(index=data_source, id=id)
            return response["_source"]
        except NotFoundError:
            return None

    async def search(self,
                     data_source: str,
                     search_query: IElasticQuery) -> List[Dict[str, Any]]:
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
        resp = await self.client.count(index=data_source)
        return resp["count"]


es_client: Optional[AsyncElasticsearch] = None


# Функция понадобится при внедрении зависимостей
async def get_elastic_client() -> AsyncElasticsearch:
    return es_client

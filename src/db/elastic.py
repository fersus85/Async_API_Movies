import logging
from typing import Optional

from elasticsearch import AsyncElasticsearch

logger = logging.getLogger(__name__)


es_client: Optional[AsyncElasticsearch] = None


# Функция понадобится при внедрении зависимостей
async def get_elastic_client() -> AsyncElasticsearch:
    return es_client

import logging
from functools import lru_cache

from elasticsearch import AsyncElasticsearch
from fastapi import Depends
from redis.asyncio import Redis

from db.elastic import get_elastic
from db.redis import cache_method, get_redis
from models.genre import Genre
from services.base import BaseService

logger = logging.getLogger(__name__)


class GenreService(BaseService):

    es_index = "genre"
    model_type = Genre

    @cache_method(cache_attr="cacher")
    async def get_total_genres_count(self) -> int:
        "Функция возвращает кол-во жанров в ES"
        resp = await self.elastic.count(index="genre")
        return resp["count"]


@lru_cache
def get_genre_service(
    cacher: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> GenreService:
    """
    Функция для создания экземпляра класса GenreService
    """
    return GenreService(cache=cacher, elastic=elastic)

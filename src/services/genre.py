import logging
from functools import lru_cache
from typing import List, Optional

from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends
from redis.asyncio import Redis

from db.elastic import get_elastic
from db.redis import get_redis, redis_cache_method
from models.genre import Genre

logger = logging.getLogger(__name__)


class GenreService:

    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self._redis = redis
        self.elastic = elastic

    @redis_cache_method(redis_attr='_redis')
    async def get_genre_by_id(self, genre_id: str) -> Optional[Genre]:
        """
        Функция для получения инф-ии о жанре по genre_id.
        Используется в API /api/v1/genres/{genre_id}
        Параметры:
          :genre_id: str UUID жанра
        Возвращает: инф-ию о жанре
        """

        logger.debug("get_genre_by_id: %s", genre_id)

        genre = await self._get_from_es_by_id(genre_id)

        if not genre:
            return None

        return genre

    async def _get_from_es_by_id(self, genre_id: str) -> Optional[Genre]:
        """
        Функция для получения из Эластика инф-ии о жанре по genre_id.
        Параметры:
          :genre_id: str UUID жанра
        Возвращает: инф-ию о жанре
        """

        logger.debug("_get_from_es_by_id: %s", genre_id)

        try:
            doc = await self.elastic.get(index="genre", id=genre_id)
        except NotFoundError:
            return None

        return Genre(**doc["_source"])

    @redis_cache_method(redis_attr='_redis')
    async def get_genres(self,
                         page_size: int,
                         page_number: int) -> List[Genre]:
        """
        Функция для получения списка жанров.
        Используется в API /api/v1/genres
        Параметры:
          :page_size: int Кол-во персон в выдаче
          :page_number: int Номер страницы выдачи
        Возвращает: список жанров
        """
        logger.debug(
            "get_genres,page_size: %s, page_number: %s", page_size, page_number
        )
        genres = await self._get_genres_from_es(page_size, page_number)
        return genres

    async def _get_genres_from_es(
        self, page_size: int, page_number: int
    ) -> List[Genre]:
        """
        Функция для получения из Эластика списка жанров.
        Параметры:
          :page_size: int Кол-во персон в выдаче
          :page_number: int Номер страницы выдачи
        Возвращает: список жанров
        """

        logger.debug(
            "_get_genres_from_es, page_size: %s, page_number: %s",
            page_size,
            page_number,
        )

        offset = (page_number - 1) * page_size

        query = {"query": {"match_all": {}}, "from": offset, "size": page_size}

        try:
            response = await self.elastic.search(index="genre", body=query)
            genres = [
                Genre(**hit["_source"]) for hit in response["hits"]["hits"]
                ]

        except NotFoundError:
            return []

        return genres

    @redis_cache_method(redis_attr='_redis')
    async def get_total_genres_count(self) -> int:
        'Функция возвращает кол-во жанров в ES'
        resp = await self.elastic.count(index='genre')
        return resp['count']


@lru_cache
def get_genre_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> GenreService:
    """
    Функция для создания экземпляра класса GenreService
    """
    return GenreService(redis=redis, elastic=elastic)

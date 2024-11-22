import logging
from functools import lru_cache
from typing import List, Optional

from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends
from redis.asyncio import Redis

from db.elastic import get_elastic
from db.redis import cache_method, get_redis
from models.film import Film
from services.base import BaseService

from .film_queries import get_query_for_popular_films

logger = logging.getLogger(__name__)


class FilmService(BaseService):

    es_index = "film"
    model_type = Film

    @cache_method(cache_attr="cacher")
    async def get_popular_films(
        self, sort: str, page_size: int, page_number: int, genre: Optional[str]
    ) -> List:
        """
        Функция для получения из ES списка популярных фильмов
        Параметры:
          :sort: str Поле для сортировки выдачи
          :genre: str Поле для фильтрации по жанру
          :page_size: int Кол-во фильмов в выдаче
          :page_number: int Номер страницы выдачи
        Возвращает:
        Список с фильмами
        """
        films = await self._get_films_from_es(
            sort, page_size, page_number, genre
        )
        return films

    @cache_method(cache_attr="cacher")
    async def get_total_films_count(self) -> int:
        "Функция возвращает кол-во фильмов в ES"
        resp = await self.elastic.count(index="film")
        return resp["count"]

    async def _get_films_from_es(
        self, sort: str, page_size: int, page_number: int, genre: Optional[str]
    ) -> List:
        """
        Функция отправляет запрос в Elastic Search,
        ищет фильмы в БД.
        Параметры
          :sort: str Поле для сортировки выдачи
          :genre: str Поле для фильтрации по жанру
          :page_size: int Кол-во фильмов в выдаче
          :page_number: int Номер страницы выдачи
        Возвращает:
        Список с фильмами
        """
        query = await get_query_for_popular_films(
            sort, page_size, page_number, genre
        )
        try:
            logger.debug("query: %s", query)
            response = await self.elastic.search(index="film", body=query)
            logger.debug("Validating response from ES")
            films = [
                Film(**hit["_source"]) for hit in response["hits"]["hits"]
            ]
        except NotFoundError:
            return []
        return films


@lru_cache
def get_film_service(
    cacher: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmService:
    """
    Функция для создания экземпляра класса FilmService
    """
    return FilmService(cache=cacher, elastic=elastic)

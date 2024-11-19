from functools import lru_cache
import logging
from typing import Optional, List

from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends
from redis.asyncio import Redis

from db.elastic import get_elastic
from db.redis import get_redis, redis_cache_method
from models.film import Film
from .film_queries import get_query_for_searching, get_query_for_popular_films


logger = logging.getLogger(__name__)


class FilmService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self._redis = redis
        self.elastic = elastic

    @redis_cache_method(redis_attr='_redis')
    async def films_search(self,
                           query: str,
                           page_size: int,
                           page_number: int) -> List:
        '''
        Функция для получения из ES списка фильмов,
        найденных по ключевому слову.
        Параметры:
        :query: str Ключевое слово для поиска
        :page_size: int Кол-во фильмов в выдаче
        :page_number: int Номер страницы выдачи
        Возвращает:
        Список найденных фильмов
        '''
        result = await self._search_films_in_es(query, page_size, page_number)
        return result

    @redis_cache_method(redis_attr='_redis')
    async def get_film_by_id(self, film_id: str) -> Optional[Film]:
        '''
        Функция для получения из ES фильма по id.
        Параметры:
        :film_id: str Id фильма
        Возвращает:
        Модель Film
        '''
        film = await self._get_from_es_by_id(film_id)
        if not film:
            return None
        return film

    @redis_cache_method(redis_attr='_redis')
    async def get_popular_films(self,
                                sort: str,
                                page_size: int,
                                page_number: int,
                                genre: Optional[str]
                                ) -> List:
        '''
        Функция для получения из ES списка популярных фильмов
        Параметры:
        :sort: str Поле для сортировки выдачи
        :genre: str Поле для фильтрации по жанру
        :page_size: int Кол-во фильмов в выдаче
        :page_number: int Номер страницы выдачи
        Возвращает:
        Возвращает:
        Список с фильмами
        '''
        films = await self._get_films_from_es(
            sort, page_size, page_number, genre
            )
        return films

    @redis_cache_method(redis_attr='_redis')
    async def get_total_films_count(self) -> int:
        'Функция возвращает кол-во фильмов в ES'
        resp = await self.elastic.count(index='film')
        return resp['count']

    async def _get_films_from_es(self,
                                 sort: str,
                                 page_size: int,
                                 page_number: int,
                                 genre: Optional[str]) -> List:
        '''
        Функция отправляет запрос в Elastic Search,
        ищет фильмы в БД.
        Параметры
        :sort: str Поле для сортировки выдачи
        :genre: str Поле для фильтрации по жанру
        :page_size: int Кол-во фильмов в выдаче
        :page_number: int Номер страницы выдачи
        Возвращает:
        Список с фильмами
        '''
        query = await get_query_for_popular_films(sort, page_size,
                                                  page_number, genre)
        try:
            logger.debug('query: %s', query)
            response = await self.elastic.search(index='film', body=query)
            logger.debug('Validating response from ES')
            films = [Film(**hit['_source'])
                     for hit in response['hits']['hits']]
        except NotFoundError:
            return []
        return films

    async def _get_from_es_by_id(self, film_id: str) -> Optional[Film]:
        '''
        Функция отправляет запрос в Elastic Search,
        ищет фильм по id в БД.
        Параметры:
        :film_id: str Id фильма
        Возвращает:
        Модель Film
        '''
        try:
            doc = await self.elastic.get(index='film', id=film_id)
        except NotFoundError:
            return None
        return Film(**doc['_source'])

    async def _search_films_in_es(self,
                                  query: str,
                                  page_size: int,
                                  page_number: int) -> List:
        '''
        Функция отправляет запрос в Elastic Search.
        Параметры:
        :query: str Ключевое слово для поиска
        :page_size: int Кол-во фильмов в выдаче
        :page_number: int Номер страницы выдачи
        Возвращает:
        Список найденных фильмов
        '''
        es_query = await get_query_for_searching(query, page_size, page_number)
        try:
            logger.debug('Query: %s', es_query)
            response = await self.elastic.search(index='film', body=es_query)
            logger.debug('Validating response from ES')
            films = [Film(**hit['_source'])
                     for hit in response['hits']['hits']]
        except NotFoundError:
            return []
        return films


@lru_cache
def get_film_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmService:
    '''
    Функция для создания экземпляра класса FilmService
    '''
    return FilmService(redis=redis, elastic=elastic)

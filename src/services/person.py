import logging
from functools import lru_cache
from typing import List, Optional

from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends
from redis.asyncio import Redis

from db.elastic import get_elastic
from db.redis import get_redis, redis_cache_method
from models.film import Film, FilmShort
from models.person import Person
from utils.film_utils import convert_films_to_person_films

from .person_queries import (get_query_for_films_by_person_id,
                             get_query_for_search_persons)

logger = logging.getLogger(__name__)


class PersonService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self._redis = redis
        self.elastic = elastic

    @redis_cache_method(redis_attr='_redis')
    async def get_person_by_id(self, person_id: str) -> Optional[Person]:
        """
        Функция для получения Персоны по person_id,
        Используется в API /api/v1/persons/{person_id}
        Параметры:
          :person_id: str UUID персоны
        Возвращает: инф-ию о персоне и фильмы с её участием.
        """

        logger.debug("get_person_by_id: %s", person_id)

        try:
            doc = await self.elastic.get(index="person", id=person_id)
        except NotFoundError:
            return None

        person_films = await self._get_films_from_es_by_person_id(person_id)
        films = await convert_films_to_person_films(person_id, person_films)

        doc["_source"]["films"] = films

        logger.debug("get_person_by_id: validating response from ES")

        person = Person(**doc["_source"])

        return person

    @redis_cache_method(redis_attr='_redis')
    async def get_films_by_person_id(
        self, person_id: str, page_size: int = 50, page_number: int = 1
    ) -> List[FilmShort]:
        """
        Функция для получения фильмов по person_id,
        Используется в API /api/v1/persons/{person_id}/film
        Параметры:
          :person_id: str UUID персоны
          :page_size: int Кол-во фильмов в выдаче
          :page_number: int Номер страницы выдачи
        Возвращает: список фильмов с участием запрошенной персоны.
        """

        logger.debug("get_films_by_person_id: %s", person_id)

        person_films = await self._get_films_from_es_by_person_id(
            person_id, page_size, page_number
        )

        filmshort_list = [
            FilmShort(uuid=pf.id, title=pf.title, imdb_rating=pf.imdb_rating)
            for pf in person_films
        ]

        return filmshort_list

    @redis_cache_method(redis_attr='_redis')
    async def _get_films_es_by_person_id(
        self, person_id: str, page_size: int = 50, page_number: int = 1
    ) -> List[Film]:
        """
        Вспомогательная функция для получения фильмов по person_id,
        Параметры:
          :person_id: str UUID персоны
          :page_size: int Кол-во фильмов в выдаче
          :page_number: int Номер страницы выдачи
        Возвращает: список фильмов с участием запрошенной персоны.
        """

        logger.debug("_get_films_from_es_by_person_id: %s", person_id)

        query = await get_query_for_films_by_person_id(
            person_id, page_size, page_number
        )

        try:

            response = await self.elastic.search(index="film", body=query)

            logger.debug(
                "_get_films_from_es_by_person_id: validating response from ES"
                )

            films = [
                Film(**hit["_source"]) for hit in response["hits"]["hits"]
                ]

        except NotFoundError:

            return []

        return films

    @redis_cache_method(redis_attr='_redis')
    async def search_persons(
        self, query: str, page_size: int, page_number: int
    ) -> List[Person]:
        """
        Функция для поиска персон по имени.
        Поиск осуществляется по полю full_name.
        Используется в API /api/v1/persons/search
        Параметры:
          :query: str Ключевое слово для поиска
          :page_size: int Кол-во персон в выдаче
          :page_number: int Номер страницы выдачи
        Возвращает: список найденных персон.
        """

        logger.debug("search_persons, query: %s", query)

        query = await get_query_for_search_persons(query,
                                                   page_size,
                                                   page_number)

        persons = []

        try:

            response = await self.elastic.search(index="person", body=query)

            for hit in response["hits"]["hits"]:

                person_id = hit["_source"]["id"]
                person_full_name = hit["_source"]["full_name"]

                person_films = await self._get_films_es_by_person_id(person_id)
                films = await convert_films_to_person_films(person_id,
                                                            person_films)

                logger.debug("search_persons: validating response from ES")

                person = Person(id=person_id, full_name=person_full_name,
                                films=films)

                persons.append(person)

        except NotFoundError:

            return []

        return persons


@lru_cache
def get_person_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> PersonService:
    """
    Функция для создания экземпляра класса PersonService
    """
    return PersonService(redis=redis, elastic=elastic)

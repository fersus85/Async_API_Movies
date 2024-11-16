import logging
from functools import lru_cache
from typing import Dict, List

from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends
from redis.asyncio import Redis

from db.elastic import get_elastic
from db.redis import cache_method, get_redis
from models.film import Film, FilmShort
from models.person import Person, PersonFilm
from services.base import BaseService

from .person_queries import get_query_for_films_by_person_id

logger = logging.getLogger(__name__)


class PersonService(BaseService):

    es_index = "person"
    model_type = Person

    async def _enrich_doc_from_es(self, doc: Dict, person_id: str):
        "Обогащаем данные о персоне списком фильмов с её участием"
        films = await self._get_person_films(person_id)
        doc["_source"]["films"] = films
        return doc

    async def _enrich_list_from_es(self, doclist: List):
        "Обогащаем данные о найденных персонах списком фильмов с их участием"
        for doc in doclist:
            films = await self._get_person_films(doc["_source"]["id"])
            doc["_source"]["films"] = films
        return doclist

    @cache_method(cache_attr="cacher")
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

    async def _get_films_from_es_by_person_id(
        self, person_id: str, page_size: int = 50, page_number: int = 1
    ) -> List[Film]:
        """
        Функция для поиска в Эластике фильмов по person_id,
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

    async def _get_person_films(self, person_id: str) -> List[PersonFilm]:
        """
        Вспомогательная функция для формирования List[PersonFilm]
          со списком roles в каждом фильме.
        Параметры:
          :person_id: str UUID персоны
          :person_films: List[Film] список фильмов, полученный
            из ф-ии _get_films_from_es_by_person_id(person_id)
        Возвращает: список PersonFilm.
        """

        person_films = await self._get_films_from_es_by_person_id(person_id)

        films = []

        for person_film in person_films:

            roles = set()
            for pp, role in zip(
                [
                    person_film.actors,
                    person_film.directors,
                    person_film.writers,
                ],
                ["actor", "director", "writer"],
            ):
                for p in pp:
                    if str(p.id) == person_id:
                        roles.add(role)

            films.append(PersonFilm(uuid=person_film.id, roles=roles))

        return films


@lru_cache
def get_person_service(
    cacher: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> PersonService:
    """
    Функция для создания экземпляра класса PersonService
    """
    return PersonService(cache=cacher, elastic=elastic)

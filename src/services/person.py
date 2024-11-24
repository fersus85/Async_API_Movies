import logging
from functools import lru_cache
from typing import Dict, List, Any, Optional

from fastapi import Depends
from pydantic import BaseModel
from redis.asyncio import Redis

from db import get_search_engine, ISearchEngine, IQuery, QueryParams
from db.elastic import ElasticPersonQuery, ElasticFilmsByPersonIDQuery
from db.redis import cache_method, get_redis
from models.film import Film, FilmShort
from models.person import Person, PersonFilm
from services.base import BaseService

logger = logging.getLogger(__name__)


class PersonService(BaseService):
    data_source = "person"
    model_type = Person

    def _get_query(self,
                   query: str,
                   page_size: int,
                   page_number: int) -> IQuery:
        return ElasticPersonQuery(QueryParams(
            query=query,
            page_size=page_size,
            page_number=page_number
        ))

    @cache_method(cache_attr="cacher")
    async def get_by_id(self, id: str) -> Optional[BaseModel]:
        data = await self.searcher.get(data_source=self.data_source,
                                       id=id)
        if not data:
            return None

        enriched = await self._enrich_by_films(data)
        return self.model_type(**enriched)

    @cache_method(cache_attr="cacher")
    async def search(self,
                     query: str,
                     page_size: int,
                     page_number: int) -> List[BaseModel]:
        query = self._get_query(query, page_size, page_number)
        data = await self.searcher.search(self.data_source, query)

        items = []
        for row in data:
            enriched = await self._enrich_by_films(row)
            items.append(self.model_type(**enriched))

        return items

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

        person_films = await self._get_films_by_person_id(
            person_id, page_size, page_number
        )

        filmshort_list = [
            FilmShort(uuid=pf.id, title=pf.title, imdb_rating=pf.imdb_rating)
            for pf in person_films
        ]

        return filmshort_list

    async def _enrich_by_films(self, obj: Dict[str, Any]) -> Dict[str, Any]:
        obj["films"] = await self._get_person_films(obj["id"])
        return obj

    async def _get_films_by_person_id(
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

        query = ElasticFilmsByPersonIDQuery(
            QueryParams(
                query=person_id,
                page_size=page_size,
                page_number=page_number
            )
        )
        data = await self.searcher.search('film', query)

        films = [Film(**row) for row in data]

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

        person_films = await self._get_films_by_person_id(person_id)

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
    searcher: ISearchEngine = Depends(get_search_engine),
) -> PersonService:
    """
    Функция для создания экземпляра класса PersonService
    """
    return PersonService(cache=cacher, search_engine=searcher)

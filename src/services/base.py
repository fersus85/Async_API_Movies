import logging
from abc import ABC
from typing import Dict, List

from elasticsearch import AsyncElasticsearch, NotFoundError
from pydantic import BaseModel

from db.redis import AbstractCache, RedisCache, cache_method

from .film_queries import get_query_for_search_films
from .genre_queries import get_query_for_search_genres
from .person_queries import get_query_for_search_persons

logger = logging.getLogger(__name__)


class BaseService(ABC):

    es_index = ""
    model_type = BaseModel

    def __init__(self, cache: AbstractCache, elastic: AsyncElasticsearch):
        self.cacher = RedisCache(cache)
        self.elastic = elastic

    @cache_method(cache_attr="cacher")
    async def get_by_id(self, id: str):
        """
        Функция для получения инф-ии об объекте по его id.
        Параметры:
          :id: str UUID объекта
        """

        logger.debug("get_by_id: %s", id)

        data = await self._get_from_es_by_id(id)

        if not data:
            return None

        data = await self._enrich_doc_from_es(data, id)

        return self.model_type(**data["_source"])

    async def _get_from_es_by_id(self, id: str):
        """
        Функция для получения из Эластика инф-ии об объекте по его id.
        Параметры:
          :id: str UUID жанра
        """

        logger.debug("_get_from_es_by_id: %s", id)

        try:
            doc = await self.elastic.get(index=self.es_index, id=id)
            return doc
        except NotFoundError:
            return None

    async def _enrich_doc_from_es(self, doc: Dict, id: str) -> Dict:
        "Обогащает полученный документ дополнительными данными"
        return doc

    async def _enrich_list_from_es(self, doclist: List) -> List[Dict]:
        "Обогащает полученный список документов дополнительными данными"
        return doclist

    async def _search_in_es(
        self, query: str, page_size: int, page_number: int
    ):
        """
        Функция поиска в Эластике.
        Параметры:
          :query: str Ключевое слово для поиска
          :page_size: int Кол-во элементов на странице
          :page_number: int Номер страницы выдачи
        Возвращает: список найденных элементов.
        """

        logger.debug("elastic search, query: %s", query)

        query = await get_query_for_search(
            self.es_index, query, page_size, page_number
        )

        try:
            response = await self.elastic.search(
                index=self.es_index, body=query
            )
        except NotFoundError:
            return []

        return response

    @cache_method(cache_attr="cacher")
    async def search(self, query: str, page_size: int, page_number: int):
        """
        Функция поиска, вызывающая поиск в Эластике и обогащающая результат.
        Параметры:
          :query: str Ключевое слово для поиска
          :page_size: int Кол-во элементов на странице
          :page_number: int Номер страницы выдачи
        Возвращает: список найденных элементов заданного класса.
        """

        logger.debug("search, query: %s", query)

        response = await self._search_in_es(query, page_size, page_number)

        response = await self._enrich_list_from_es(response["hits"]["hits"])

        items = [self.model_type(**hit["_source"]) for hit in response]

        return items


async def get_query_for_search(
    es_index: str, query: str, page_size: int, page_number: int
) -> Dict:
    """
    Функция, в зав-ти от класса/индекса, формирующая текст поиска в Эластике.
    Параметры:
      :es_index: str Индекс Эластика (genre/person/film)
      :query: str Ключевое слово для поиска
      :page_size: int Кол-во элементов на странице
      :page_number: int Номер страницы выдачи
    Возвращает: Возвращает запрос в формате dict.
    """
    query_function_map = {
        "genre": get_query_for_search_genres,
        "person": get_query_for_search_persons,
        "film": get_query_for_search_films,
    }

    if es_index not in query_function_map:
        raise ValueError(f"Неизвестный индекс: {es_index}")

    query_function = query_function_map[es_index]

    return await query_function(query, page_size, page_number)

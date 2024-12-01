import logging
from functools import lru_cache
from typing import List, Optional

from fastapi import Depends

from db.redis import cache_method
from db.searcher import query_factory, IQuery, get_search_engine, ISearchEngine
from db.searcher.query import PopularFilmQuery, FilmQuery
from db.cacher import AbstractCache, get_cacher
from models.film import Film
from models.query_params import SortableQueryParams, QueryParams
from services.base import BaseService

logger = logging.getLogger(__name__)


class FilmService(BaseService):

    data_source = "film"
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
        params = SortableQueryParams(
            query=genre,
            page_size=page_size,
            page_number=page_number,
            sort=sort
        )
        query = query_factory(self.searcher, PopularFilmQuery, params)

        data = await self.searcher.search(self.data_source, query)

        films = [Film(**row) for row in data]

        return films

    async def get_total_films_count(self) -> int:
        """Функция возвращает кол-во фильмов в ES"""
        return await self.get_count()

    def _get_query(self,
                   query: str,
                   page_size: int,
                   page_number: int) -> IQuery:
        params = QueryParams(
            query=query,
            page_size=page_size,
            page_number=page_number
        )

        return query_factory(self.searcher, FilmQuery, params)


@lru_cache
def get_film_service(
    cacher: AbstractCache = Depends(get_cacher),
    searcher: ISearchEngine = Depends(get_search_engine),
) -> FilmService:
    """
    Функция для создания экземпляра класса FilmService
    """
    return FilmService(cache=cacher, search_engine=searcher)

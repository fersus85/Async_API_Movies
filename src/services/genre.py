import logging
from functools import lru_cache

from fastapi import Depends

from db.redis import cache_method
from db.searcher import IQuery, query_factory, get_search_engine, ISearchEngine
from db.searcher.query import GenreQuery
from db.cacher import AbstractCache, get_cacher
from models.genre import Genre
from models.query_params import QueryParams
from services.base import BaseService


logger = logging.getLogger(__name__)


class GenreService(BaseService):

    data_source = "genre"
    model_type = Genre

    @cache_method(cache_attr="cacher")
    async def get_total_genres_count(self) -> int:
        "Функция возвращает кол-во жанров в ES"
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

        return query_factory(self.searcher, GenreQuery, params)


@lru_cache
def get_genre_service(
    cacher: AbstractCache = Depends(get_cacher),
    searcher: ISearchEngine = Depends(get_search_engine),
) -> GenreService:
    """
    Функция для создания экземпляра класса GenreService
    """
    return GenreService(cache=cacher, search_engine=searcher)

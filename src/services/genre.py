import logging
from functools import lru_cache

from fastapi import Depends
from redis.asyncio import Redis

from db import get_search_engine, ISearchEngine, IQuery, QueryParams
from db.elastic import ElasticGenreQuery
from db.redis import cache_method, get_redis
from models.genre import Genre
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
        return ElasticGenreQuery(QueryParams(
            query=query,
            page_size=page_size,
            page_number=page_number
        ))


@lru_cache
def get_genre_service(
    cacher: Redis = Depends(get_redis),
    searcher: ISearchEngine = Depends(get_search_engine),
) -> GenreService:
    """
    Функция для создания экземпляра класса GenreService
    """
    return GenreService(cache=cacher, search_engine=searcher)

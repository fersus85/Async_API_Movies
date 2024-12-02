import abc
import logging
from typing import List, Optional

from pydantic import BaseModel

from db.redis import AbstractCache, cache_method
from db.searcher import ISearchEngine, IQuery

logger = logging.getLogger(__name__)


class BaseService(abc.ABC):
    data_source = ""
    model_type = BaseModel

    def __init__(self, cache: AbstractCache, search_engine: ISearchEngine):
        self.cacher = cache
        self.searcher = search_engine

    @abc.abstractmethod
    def _get_query(
        self, query: str, page_size: int, page_number: int
    ) -> IQuery:
        pass

    @cache_method(cache_attr="cacher")
    async def search(
        self, query: str, page_size: int, page_number: int
    ) -> List[BaseModel]:
        """
        Функция поиска, вызывающая поиск в Эластике и обогащающая результат.
        Параметры:
          :query: str Ключевое слово для поиска
          :page_size: int Кол-во элементов на странице
          :page_number: int Номер страницы выдачи
        Возвращает: список найденных элементов заданного класса.
        """
        query = self._get_query(query, page_size, page_number)
        data = await self.searcher.search(self.data_source, query)

        items = [self.model_type(**row) for row in data]

        return items

    @cache_method(cache_attr="cacher")
    async def get_by_id(self, id: str) -> Optional[BaseModel]:
        """
        Функция для получения инф-ии об объекте по его id.
        Параметры:
          :id: str UUID объекта
        """

        data = await self.searcher.get(data_source=self.data_source, id=id)
        if not data:
            return None

        return self.model_type(**data)

    @cache_method(cache_attr="cacher")
    async def get_count(self) -> int:
        return await self.searcher.count(self.data_source)

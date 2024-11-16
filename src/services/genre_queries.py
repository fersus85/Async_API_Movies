from typing import Dict


async def get_query_for_search_genres(
    query: str, page_size: int, page_number: int
) -> Dict:
    """
    Функция формирует запрос в Elastic Search
    Параметры:
      :query: str Ключевое слово для поиска
      :page_size: int Кол-во фильмов в выдаче
      :page_number: int Номер страницы выдачи
    Возвращает: dict
    Запрос в БД в формате словаря
    """

    offset = (page_number - 1) * page_size

    query = {"query": {"match_all": {}}, "from": offset, "size": page_size}

    return query

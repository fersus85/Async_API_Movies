from typing import Dict


async def get_query_for_search_persons(
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

    query = {
        "query": {"match": {"full_name": query}},
        "from": offset,
        "size": page_size,
    }

    return query


async def get_query_for_films_by_person_id(
    person_id: str, page_size: int, page_number: int
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

    query = {
        "query": {
            "bool": {
                "should": [
                    {
                        "nested": {
                            "path": "actors",
                            "query": {"term": {"actors.id": person_id}},
                        }
                    },
                    {
                        "nested": {
                            "path": "writers",
                            "query": {"term": {"writers.id": person_id}},
                        }
                    },
                    {
                        "nested": {
                            "path": "directors",
                            "query": {"term": {"directors.id": person_id}},
                        }
                    },
                ]
            }
        },
        "from": offset,
        "size": page_size,
    }

    return query

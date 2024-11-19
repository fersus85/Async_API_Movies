from typing import Dict, Optional


async def get_query_for_searching(query: str,
                                  page_size: int,
                                  page_number: int) -> Dict:
    '''
    Функция формирует запрос в Elastic Search
    Параметры:
    :query: str Ключевое слово для поиска
    :page_size: int Кол-во фильмов в выдаче
    :page_number: int Номер страницы выдачи
    Возвращает: dict
    Запрос в БД в формате словаря
    '''
    offset = (page_number - 1) * page_size
    es_query = {
        'query': {
            'multi_match': {
                'query': query,
                'fields': [
                    'title', 'directors',
                    'actors', 'writers'
                    ],
                'type': 'best_fields'
            }
        },
        'from': offset,
        'size': page_size
        }
    return es_query


async def get_query_for_popular_films(sort: str,
                                      page_size: int,
                                      page_number: int,
                                      genre: Optional[str]) -> Dict:
    '''
    Функция формирует запрос в Elastic Search
    Параметры:
    :sort: str Поле для сортировки выдачи
    :page_size: int Кол-во фильмов в выдаче
    :page_number: int Номер страницы выдачи
    :genre: str Поле для фильтрации по жанру
    Возвращает: dict
    Запрос в БД в формате словаря
    '''
    offset = (page_number - 1) * page_size
    order = 'desc' if sort.startswith('-') else 'asc'
    sort_field = sort.lstrip('-')
    query = {
        'query': {
            'bool': {
                'must': [
                    {
                        'match_all': {}
                    }
                ]
            }
        },
        'sort': [
            {
                sort_field: {
                    'order': order
                }
            }
        ],
        'from': offset,
        'size': page_size
    }
    if genre:
        query['query']['bool']['filter'] = [
            {
                'nested': {
                    'path': 'genres',
                    'query': {
                        'term': {'genres.id': genre}
                        }
                }
            }
        ]
    return query

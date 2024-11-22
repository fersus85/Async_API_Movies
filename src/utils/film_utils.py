from typing import List

from schemas.film import FilmSchema


async def get_response_list(lst: List) -> List:
    """
    Формирует список ответов на основе входного списка объектов.
    """
    resp_list = [
        FilmSchema(uuid=hit.id, title=hit.title, imdb_rating=hit.imdb_rating)
        for hit in lst
    ]
    return resp_list

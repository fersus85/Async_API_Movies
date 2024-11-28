from typing import List
from http import HTTPStatus

from fastapi import HTTPException

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


def validate_page_number(page_number: int, max_pages: int) -> None:
    if page_number > max_pages:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=f"Страница: {page_number} превысила максимум: {max_pages}",
        )

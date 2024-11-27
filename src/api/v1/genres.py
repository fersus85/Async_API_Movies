from http import HTTPStatus
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query

from schemas.genre import GenreSchema
from services.genre import GenreService, get_genre_service
import utils.response_getter as rg
from utils.film_utils import validate_page_number

router = APIRouter()


@router.get(
    "/",
    response_model=List[GenreSchema],
    summary="Все жанры",
    description="Возвращает все жанры из базы данных",
    responses=rg.get_genres_response()
)
async def get_genres(
    page_size: int = Query(
        50, ge=1, le=50, description="Кол-во жанров в выдаче (1-50)"
    ),
    page_number: int = Query(1, ge=1, description="Номер страницы выдачи"),
    genre_service: GenreService = Depends(get_genre_service),
) -> List[GenreSchema]:
    """
    Обработчик маршрута api/v1/genres,
    """
    total = await genre_service.get_total_genres_count()

    max_pages = (total + page_size - 1) // page_size

    validate_page_number(page_number, max_pages)

    genre_list = await genre_service.search("", page_size, page_number)

    resp_list = [
        GenreSchema(
            uuid=genre.id, name=genre.name, description=genre.description
        )
        for genre in genre_list
    ]

    return resp_list


@router.get(
    "/{genre_id}/",
    response_model=GenreSchema,
    summary="Поиск жанра по id",
    description="Ищет в базе данных ES жанр по переданному id",
    responses=rg.genres_by_id_response()
)
async def get_genre_by_id(
    genre_id: str, genre_service: GenreService = Depends(get_genre_service)
) -> GenreSchema:
    """
    Обработчик маршрута api/v1/genres/{genre_id},

    - **genre_id**: ID жанра, который нужно получить.
    """
    genre = await genre_service.get_by_id(genre_id)

    if not genre:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Genre not found"
        )

    return GenreSchema(
        uuid=genre.id, name=genre.name, description=genre.description
    )

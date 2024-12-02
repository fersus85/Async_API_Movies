import logging
from http import HTTPStatus
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from schemas.film import FilmDetailSchema, FilmPerson, FilmSchema, GenreFilm
from services.film import FilmService, get_film_service
from utils.film_utils import get_response_list, validate_page_number
import utils.response_getter as rg

logger = logging.getLogger(__name__)

router = APIRouter()

VALID_SORT_OPT = (
    "-imdb_rating",
    "imdb_rating",
    "-title",
    "title",
    "-creation_date",
    "creation_date",
)


@router.get(
    "/search",
    response_model=List[FilmSchema],
    summary="Поиск фильмов",
    description="Полнотекстовый поиск по кинопроизведениям, \
                поля для поиска: title, directors, actors, writers",
    responses=rg.search_film_response(),
)
async def search_in_films(
    query: str = Query(..., description="Ключевое слово для поиска"),
    page_size: int = Query(
        50, ge=1, le=50, description="Кол-во фильмов в выдаче (1-50)"
    ),
    page_number: int = Query(1, ge=1, description="Номер страницы выдачи"),
    film_service: FilmService = Depends(get_film_service),
) -> List[FilmSchema]:
    """
    Обработчик маршрута api/v1/films/search,
    ищет фильмы в БД по ключевому слову
    Параметры:
      :query: str Ключевое слово для поиска
      :page_size: int Кол-во фильмов в выдаче
      :page_number: int Номер страницы выдачи
      :film_service: Сервис, управляющий извлечением данных из ES
    Возвращает:
    Модель PopularFilmsSchema - список с вложенными фильмами
    """
    if not query:
        return []
    total = await film_service.get_total_films_count()
    max_pages = (total + page_size - 1) // page_size
    validate_page_number(page_number, max_pages)

    logger.debug("Start searching by query")
    result = await film_service.search(query, page_size, page_number)
    if not result:
        return []

    logger.debug("Start creating response list")
    resp_list: List[FilmSchema] = await get_response_list(lst=result)

    logger.debug("Returning popular films")
    return resp_list


@router.get(
    "/",
    response_model=List[FilmSchema],
    summary="Популярные фильмы",
    description="Возращает сортированные фильмы\
                  с возможностью фильтрации по жанру",
    responses=rg.get_film_list_response(),
)
async def get_popular_films(
    sort: str = "-imdb_rating",
    genre_id: Optional[str] = None,
    page_size: int = Query(
        50, ge=1, le=50, description="Кол-во фильмов в выдаче (1-50)"
    ),
    page_number: int = Query(1, ge=1, description="Номер страницы выдачи"),
    film_service: FilmService = Depends(get_film_service),
) -> List[FilmSchema]:
    """
    Обработчик маршрута api/v1/films,
    ищет фильмы в БД. Есть возможность фильтровать по жанрам.
    Параметры:
      :sort: str Поле для сортировки выдачи
      :genre_id: str UUID жанра для фильтрации
      :page_size: int Кол-во фильмов в выдаче
      :page_number: int Номер страницы выдачи
      :film_service: Сервис, управляющий извлечением данных из ES
    Возвращает:
    Модель PopularFilmsSchema - список с вложенными фильмами
    """
    total = await film_service.get_total_films_count()
    max_pages = (total + page_size - 1) // page_size
    validate_page_number(page_number, max_pages)

    if sort not in VALID_SORT_OPT:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=f"Недопустимое поле: {sort}. Допустимые: {VALID_SORT_OPT}",
        )
    logger.debug("Start searching popular films")
    result = await film_service.get_popular_films(
        sort, page_size, page_number, genre_id
    )
    logger.debug("Start creating response list")
    if not result:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Films not found"
        )
    resp_list: List[FilmSchema] = await get_response_list(lst=result)
    logger.debug("Returning popular films")
    return resp_list


@router.get(
    "/{film_id}/",
    response_model=FilmDetailSchema,
    summary="Находит фильм по id",
    description="Находит фильм по id и возвращает \
                детальную информацию о нем",
    responses=rg.get_film_by_id_response(),
)
async def get_film_by_id(
    film_id: str, film_service: FilmService = Depends(get_film_service)
) -> FilmDetailSchema:
    """
    Обработчик маршрута api/v1/films{film_id},
    ищет фильм по id в БД.
    Параметры:
      :film_id: str Id фильма
      :film_service: Сервис, управляющий извлечением данных из ES
    Возвращает:
    Модель FilmDetailSchema
    """
    logger.debug("Start searching film by id")
    film = await film_service.get_by_id(film_id)
    if not film:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Film not found"
        )
    logger.debug("Returning info about film")
    return FilmDetailSchema(
        uuid=film.id,
        title=film.title,
        description=film.description,
        imdb_rating=film.imdb_rating,
        genre=[
            GenreFilm(uuid=genre.id, name=genre.name) for genre in film.genres
        ],
        actors=[
            FilmPerson(uuid=pers.id, full_name=pers.full_name)
            for pers in film.actors
        ],
        writers=[
            FilmPerson(uuid=pers.id, full_name=pers.full_name)
            for pers in film.writers
        ],
        directors=[
            FilmPerson(uuid=pers.id, full_name=pers.full_name)
            for pers in film.directors
        ],
    )

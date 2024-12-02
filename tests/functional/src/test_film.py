import pickle
from http import HTTPStatus
from typing import Any, Callable, Dict
from urllib.parse import urlencode
from uuid import uuid4

import pytest
from aiohttp import ClientResponse
from db.redis import form_key
from models.film import Film
from redis.asyncio import Redis
from tests.functional.settings import test_settings


@pytest.mark.parametrize(
    "query_data, exp_answer",
    [
        (
            "3d825f60-9fff-4dfe-b294-1a45fa1e115d",
            {
                "status": HTTPStatus.OK,
                "title": "Star Wars: Episode IV - A New Hope",
                "imdb_rating": 8.6,
            },
        ),
        (
            "qwea21cf-9097-479e-904a-13dd7198c1dd",
            {
                "status": HTTPStatus.NOT_FOUND,
                "title": None,
                "imdb_rating": None,
            },
        ),
        (
            "INCORRECT-UUID-FORMAT",
            {
                "status": HTTPStatus.NOT_FOUND,
                "title": None,
                "imdb_rating": None,
            },
        ),
        (
            "/",
            {
                "status": HTTPStatus.NOT_FOUND,
                "title": None,
                "imdb_rating": None,
            },
        ),
    ],
)
@pytest.mark.asyncio
async def test_get_film_by_id(
    make_get_request: Callable[[str, str], ClientResponse],
    query_data: str,
    exp_answer: Dict[str, Any],
):
    """
    Тестирует получение информации о фильме по его ID.

    Проверяет следующие сценарии:
    - Успешный запрос с корректным ID.
    - Запрос с несуществующим ID, который возвращает статус NOT_FOUND.
    - Запрос с некорректным форматом ID, который возвращает статус NOT_FOUND.

    :param make_get_request: Фикстура для выполнения GET-запроса.
    :param query_data: ID для запроса.
    :param exp_answer: Ожидаемый ответ, содержащий статус и название фильма.
    """
    response = await make_get_request(test_settings.ES_FILM_IDX, query_data)

    body = await response.json()
    status = response.status

    assert status == exp_answer.get("status")
    assert body.get("title") == exp_answer.get("title")
    assert body.get("imdb_rating") == exp_answer.get("imdb_rating")


@pytest.mark.asyncio
async def test_list_films(
    make_get_request: Callable[[str, str], ClientResponse]
):
    """
    Тестирует получение всех загруженных для теста фильмов.

    :param make_get_request: Фикстура для выполнения GET-запроса.
    """
    response = await make_get_request(test_settings.ES_FILM_IDX, "")

    body = await response.json()
    status = response.status

    assert len(body) == 6
    assert status == HTTPStatus.OK


@pytest.mark.parametrize(
    "query_data, exp_answer",
    [
        (
            {"page_size": 30, "page_number": 1},
            {"status": HTTPStatus.OK, "body_len": 6},
        ),
        (
            {"page_size": 5, "page_number": 1},
            {"status": HTTPStatus.OK, "body_len": 5},
        ),
        (
            {"page_size": 5, "page_number": 2},
            {"status": HTTPStatus.OK, "body_len": 1},
        ),
        (
            {"page_size": 5, "page_number": 3},
            {"status": HTTPStatus.BAD_REQUEST, "body_len": 1},
        ),
        (
            {"page_size": 51, "page_number": 1},
            {"status": HTTPStatus.UNPROCESSABLE_ENTITY, "body_len": 1},
        ),
        (
            {"page_size": 0, "page_number": 0},
            {"status": HTTPStatus.UNPROCESSABLE_ENTITY, "body_len": 1},
        ),
        (
            {"page_size": -1, "page_number": -1},
            {"status": HTTPStatus.UNPROCESSABLE_ENTITY, "body_len": 1},
        ),
    ],
)
@pytest.mark.asyncio
async def test_list_films_with_pages(
    make_get_request: Callable[[str, str], ClientResponse],
    query_data: Dict[str, Any],
    exp_answer: Dict[str, Any],
):
    """
    Тестирует пагинацию при получении списка фильмов.

    Параметры:
    - query_data (Dict): Параметры запроса для пагинации.
    - exp_answer (Dict): Ожидаемый ответ, со статусом и длиной списка фильмов.
    """
    query_parameters = f"?{urlencode(query_data)}"

    response = await make_get_request(
        test_settings.ES_FILM_IDX, query_parameters
    )

    body = await response.json()
    status = response.status

    assert status == exp_answer.get("status")
    assert len(body) == exp_answer.get("body_len")


@pytest.mark.parametrize(
    "query_data, exp_answer",
    [
        (
            {
                "sort": "-imdb_rating",
                "genre_id": "3d8d9bf5-0d90-4353-88ba-4ccc5d2c07ff",
            },
            {
                "status": HTTPStatus.OK,
                "body_len": 3,
                "film_id": "0312ed51-8833-413f-bff5-0e139c11264a",
            },
        ),
        (
            {
                "sort": "imdb_rating",
                "genre_id": "3d8d9bf5-0d90-4353-88ba-4ccc5d2c07ff",
            },
            {
                "status": HTTPStatus.OK,
                "body_len": 3,
                "film_id": "516f91da-bd70-4351-ba6d-25e16b7713b7",
            },
        ),
        (
            {
                "sort": "-imdb_rating",
                "genre_id": "5373d043-3f41-4ea8-9947-4b746c601bbd",
            },
            {
                "status": HTTPStatus.OK,
                "body_len": 3,
                "film_id": "8fcebebd-a1d9-45c9-96c5-bd798db4a9c6",
            },
        ),
        (
            {
                "sort": "imdb_rating",
                "genre_id": "5373d043-3f41-4ea8-9947-4b746c601bbd",
            },
            {
                "status": HTTPStatus.OK,
                "body_len": 3,
                "film_id": "24eafcd7-1018-4951-9e17-583e2554ef0a",
            },
        ),
    ],
)
@pytest.mark.asyncio
async def test_list_films_with_sort_and_filter(
    make_get_request: Callable[[str, str], ClientResponse],
    query_data: Dict[str, Any],
    exp_answer: Dict[str, Any],
):
    """
    Тестирует сортировку и фильтрацию при получении списка фильмов.

    Параметры:
    - query_data (Dict): Параметры сортировки и фильтрации по жанру
    - exp_answer (Dict): Ожидаемый ответ, со статусом, длиной списка фильмов
        и первым фильмом в выдаче
    """
    query_parameters = f"?{urlencode(query_data)}"

    response = await make_get_request(
        test_settings.ES_FILM_IDX, query_parameters
    )

    body = await response.json()
    first_film = body[0]
    status = response.status

    assert status == exp_answer.get("status")
    assert len(body) == exp_answer.get("body_len")
    assert first_film.get("uuid") == exp_answer.get("film_id")


@pytest.mark.asyncio
async def test_cache_film_by_id(
    make_get_request: Callable[[str, str], ClientResponse], redis_client: Redis
):
    """
    Тестирует кэширование при получении списка фильмов по его id.

    Параметры:
    - make_get_request: Фикстура для выполнения запроса к API.
    - redis_client: Фикстура Redis для работы с кэшем.

    Проверяет, что данные кэша возвращаются корректно,
    и что кэш очищается после запроса.
    """
    film_id = str(uuid4())
    key = form_key("get_by_id", (film_id,), {})
    test_film_data = Film(
        id=film_id,
        title="CACHE",
        directors=[],
        actors=[],
        writers=[],
        genres=[],
    )

    await redis_client.set(key, pickle.dumps(test_film_data), ex=60)

    response = await make_get_request(test_settings.ES_FILM_IDX, film_id)
    body = await response.json()

    assert response.status == HTTPStatus.OK
    assert body["uuid"] == film_id
    assert body["title"] == "CACHE"

    await redis_client.delete(key)

    response = await make_get_request(test_settings.ES_FILM_IDX, film_id)
    assert response.status == HTTPStatus.NOT_FOUND

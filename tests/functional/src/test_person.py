
from typing import Dict, Callable, Optional, Any, List
from http import HTTPStatus
from urllib.parse import urlencode
from uuid import uuid4
import pickle

from redis.asyncio import Redis
import pytest
from aiohttp import ClientResponse
from db.redis import form_key
from models.person import Person
from tests.functional.settings import test_settings


import pytest
from tests.functional.settings import test_settings


@pytest.mark.parametrize(
    "query_data, exp_answer",
    [
        (
            "a5a8f573-3cee-4ccc-8a2b-91cb9f55250a",
            {"status": HTTPStatus.OK, "name": "George Lucas"},
        ),
        (
            "a5a8f513-3c7e-4vcc-8a2b-91cbff55250a",
            {"status": HTTPStatus.NOT_FOUND, "name": None},
        ),
        (
            "",
            {"status": HTTPStatus.NOT_FOUND, "name": None},
        ),
        (
            "invalid-uuid-format",
            {"status": HTTPStatus.NOT_FOUND, "name": None},
        ),
    ],
)
@pytest.mark.asyncio
async def test_get_person_by_id(
    make_get_request: Callable[[str, str], ClientResponse],
    query_data: str,
    exp_answer: Dict[str, Any],
):
    """
    Тестирует получение информации о персоне по её ID.

    Проверяет следующие сценарии:
    - Успешный запрос с корректным ID персоны.
    - Запрос с несуществующим ID, который возвращает статус NOT_FOUND.
    - Запрос с пустым ID, который возвращает статус NOT_FOUND.
    - Запрос с некорректным форматом ID, который возвращает статус NOT_FOUND.

    feature/tests_person
    :param make_get_request: Фикстура для выполнения GET-запроса.
    :param query_data: ID персоны для запроса.
    :param exp_answer: Ожидаемый ответ, содержащий статус и имя персоны.
    """

    response = await make_get_request(test_settings.ES_PERSON_IDX, query_data)

    body = await response.json()
    status = response.status

    assert status == exp_answer.get("status")
    assert body.get("full_name") == exp_answer.get("name")


@pytest.mark.asyncio
async def test_get_person_by_id_film_list(
    make_get_request: Callable[[str, str], ClientResponse]
):
    """
    Тестирует получение списка фильмов для конкретной персоны по её ID.

    Проверяет, что при успешном запросе возвращается корректный список фильмов.

    :param make_get_request: Фикстура для выполнения GET-запроса.
    """
    pers_id = "a5a8f573-3cee-4ccc-8a2b-91cb9f55250a"
    films = [
        "516f91da-bd70-4351-ba6d-25e16b7713b7",
        "3d825f60-9fff-4dfe-b294-1a45fa1e115d",
        "0312ed51-8833-413f-bff5-0e139c11264a",
    ]
    response = await make_get_request(test_settings.ES_PERSON_IDX, pers_id)

    body = await response.json()
    status = response.status
    response_list = [films.get("uuid") for films in body.get("films")]
    assert status == HTTPStatus.OK
    assert response_list == films


@pytest.mark.asyncio
async def test_cache_person_by_id(
    redis_client: Redis,
    make_get_request: Callable[[str, str], ClientResponse],
):
    """
    Тестирует кэширование информации о персоне по её ID.

    Проверяет, что данные кэшируются и корректно извлекаются из кэша.
    Также проверяет, что после удаления кэша данные больше не доступны.

    :param redis_client: Фикстура для работы с Redis.
    :param make_get_request: Фикстура для выполнения GET-запроса.
    """
    person_id = str(uuid4())
    key = form_key("get_by_id", (person_id,), {})
    test_person_data = Person(id=person_id, full_name="CACHE", films=[])

    await redis_client.set(key, pickle.dumps(test_person_data), ex=60)

    response = await make_get_request(test_settings.ES_PERSON_IDX, person_id)
    body = await response.json()

    assert response.status == HTTPStatus.OK
    assert body["uuid"] == person_id
    assert body["full_name"] == "CACHE"

    await redis_client.delete(key)

    response = await make_get_request(test_settings.ES_PERSON_IDX, person_id)
    assert response.status == HTTPStatus.NOT_FOUND


@pytest.mark.parametrize(
    "query_data, exp_answer",
    [
        (
            "a5a8f573-3cee-4ccc-8a2b-91cb9f55250a",
            {
                "status": HTTPStatus.OK,
                "films": [
                    "516f91da-bd70-4351-ba6d-25e16b7713b7",
                    "3d825f60-9fff-4dfe-b294-1a45fa1e115d",
                    "0312ed51-8833-413f-bff5-0e139c11264a",
                ],
            },
        ),
        (
            "a5a8f513-3c7e-4vcc-8a2b-91cbff55250a",
            {"status": HTTPStatus.OK, "films": []},
        ),
        (
            "",
            {"status": HTTPStatus.NOT_FOUND, "detail": "Not Found"},
        ),
        (
            "invalid-uuid-format",
            {"status": HTTPStatus.OK, "films": []},
        ),
    ],
)
@pytest.mark.asyncio
async def test_get_films_by_person_id(
    make_request_persons_list: Callable[
        [str, str, Optional[str]], ClientResponse
    ],
    query_data: str,
    exp_answer: Dict[str, Any],
):
    """
    Тестирует получение списка фильмов по идентификатору персоны.

    Параметры:
    - query_data (str): Идентификатор персоны (UUID).
    - exp_answer (Dict): Ожидаемый ответ, содержащий статус и список фильмов.

    Проверяет, что статус ответа и список фильмов соответствуют ожидаемым
    значениям.
    Если в ответе присутствует поле "detail", проверяет его значение.
    """
    response = await make_request_persons_list(
        test_settings.ES_PERSON_IDX, query_data
    )

    body = await response.json()
    status = response.status
    if "detail" not in body:
        film_list = [film.get("uuid") for film in body]
        assert status == exp_answer.get("status")
        assert film_list == exp_answer.get("films")
    else:
        assert status == exp_answer.get("status")
        assert body.get("detail") == exp_answer.get("detail")


@pytest.mark.parametrize(
    "query_data, exp_answer",
    [
        (
            {"page_size": 1, "page_number": 1},
            {"status": HTTPStatus.OK, "length": 1},
        ),
        (
            {"page_size": 51, "page_number": 1},
            {"status": HTTPStatus.UNPROCESSABLE_ENTITY, "length": 1},
        ),
        (
            {"page_size": 50, "page_number": 0},
            {"status": HTTPStatus.UNPROCESSABLE_ENTITY, "length": 1},
        ),
        (
            {"page_size": 50, "page_number": 2},
            {"status": HTTPStatus.OK, "length": 0},
        ),
    ],
)
@pytest.mark.asyncio
async def test_get_films_by_person_id_pagination(
    make_request_persons_list: Callable[
        [str, str, Optional[str]], ClientResponse
    ],
    query_data: Dict[str, int],
    exp_answer: Dict[str, Any],
):
    """
    Тестирует пагинацию при получении списка фильмов по id персоны.

    Параметры:
    - query_data (Dict): Параметры запроса для пагинации.
    - exp_answer (Dict): Ожидаемый ответ, со статусом и длиной списка фильмов.

    Проверяет, что данные кэшируются и корректно извлекаются из кэша.
    Также проверяет, что после удаления кэша данные больше не доступны.
    """
    person_id = "a5a8f573-3cee-4ccc-8a2b-91cb9f55250a"
    params = f"?{urlencode(query_data)}"

    response = await make_request_persons_list(
        test_settings.ES_PERSON_IDX, person_id, params
    )

    body = await response.json()
    status = response.status

    assert status == exp_answer.get("status")
    assert len(body) == exp_answer.get("length")


@pytest.mark.asyncio
async def test_cache_get_films_by_person_id(
    make_request_persons_list: Callable[
        [str, str, Optional[str]], ClientResponse
    ],
    redis_client: Redis,
    get_short_list: List,
):
    """
    Тестирует кэширование при получении списка фильмов по id персоны.

    Параметры:
    - redis_client: Фикстура Redis для работы с кэшем.
    - make_request_persons_list: Фикстура для выполнения запроса к API.
    - get_short_list: Фикстура - список фильмов для кэширования.

    Проверяет, что данные кэша возвращаются корректно,
    и что кэш очищается после запроса
    """
    person_id = str(uuid4())
    key = form_key("get_films_by_person_id", (person_id, 50, 1), {})
    cached_data = get_short_list

    await redis_client.set(key, pickle.dumps(cached_data), ex=60)

    response = await make_request_persons_list(
        test_settings.ES_PERSON_IDX, person_id
    )
    body = await response.json()

    assert response.status == HTTPStatus.OK
    assert len(body) == len(get_short_list)

    await redis_client.delete(key)

    response = await make_request_persons_list(
        test_settings.ES_PERSON_IDX, person_id
    )
    body = await response.json()
    assert response.status == HTTPStatus.OK
    assert body == []

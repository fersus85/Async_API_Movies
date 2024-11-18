import pickle
from typing import Dict
from uuid import uuid4

import pytest
from db.redis import form_key
from models.film import Film
from tests.functional.settings import test_settings


@pytest.mark.parametrize(
    "query_data, exp_answer",
    [
        (
            "3d825f60-9fff-4dfe-b294-1a45fa1e115d",
            {
                "status": 200,
                "title": "Star Wars: Episode IV - A New Hope",
                "imdb_rating": 8.6,
            },
        ),
        (
            "qwea21cf-9097-479e-904a-13dd7198c1dd",
            {"status": 404, "title": None, "imdb_rating": None},
        ),
        (
            "INCORRECT-UUID-FORMAT",
            {"status": 404, "title": None, "imdb_rating": None},
        ),
    ],
)
@pytest.mark.asyncio
async def test_search_film_by_id(
    make_get_request, query_data: str, exp_answer: Dict
):

    response = await make_get_request(test_settings.ES_FILM_IDX, query_data)

    body = await response.json()
    status = response.status

    assert status == exp_answer.get("status")
    assert body.get("title") == exp_answer.get("title")
    assert body.get("imdb_rating") == exp_answer.get("imdb_rating")


@pytest.mark.asyncio
async def test_list_films(make_get_request):

    response = await make_get_request(test_settings.ES_FILM_IDX, "")

    body = await response.json()
    status = response.status

    assert len(body) == 6
    assert status == 200


@pytest.mark.parametrize(
    "query_data, exp_answer",
    [
        (
            {"page_size": 30, "page_number": 1},
            {"status": 200, "body_len": 6},
        ),
        (
            {"page_size": 5, "page_number": 1},
            {"status": 200, "body_len": 5},
        ),
        (
            {"page_size": 5, "page_number": 2},
            {"status": 200, "body_len": 1},
        ),
        (
            {"page_size": 5, "page_number": 3},
            {"status": 400, "body_len": 1},
        ),
        (
            {"page_size": 51, "page_number": 1},
            {"status": 422, "body_len": 1},
        ),
    ],
)
@pytest.mark.asyncio
async def test_list_films_with_pages(
    make_get_request, query_data: Dict, exp_answer: Dict
):

    page_size = query_data["page_size"]
    page_number = query_data["page_number"]

    query_parameters = f"?page_size={page_size}&page_number={page_number}"

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
                "sort_order": "-imdb_rating",
                "genre_filter": "3d8d9bf5-0d90-4353-88ba-4ccc5d2c07ff",
            },
            {
                "status": 200,
                "body_len": 3,
                "film_id": "0312ed51-8833-413f-bff5-0e139c11264a",
            },
        ),
        (
            {
                "sort_order": "imdb_rating",
                "genre_filter": "3d8d9bf5-0d90-4353-88ba-4ccc5d2c07ff",
            },
            {
                "status": 200,
                "body_len": 3,
                "film_id": "516f91da-bd70-4351-ba6d-25e16b7713b7",
            },
        ),
        (
            {
                "sort_order": "-imdb_rating",
                "genre_filter": "5373d043-3f41-4ea8-9947-4b746c601bbd",
            },
            {
                "status": 200,
                "body_len": 3,
                "film_id": "8fcebebd-a1d9-45c9-96c5-bd798db4a9c6",
            },
        ),
        (
            {
                "sort_order": "imdb_rating",
                "genre_filter": "5373d043-3f41-4ea8-9947-4b746c601bbd",
            },
            {
                "status": 200,
                "body_len": 3,
                "film_id": "24eafcd7-1018-4951-9e17-583e2554ef0a",
            },
        ),
    ],
)
@pytest.mark.asyncio
async def test_list_films_with_sort_and_filter(
    make_get_request, query_data: Dict, exp_answer: Dict
):

    sort_order = query_data["sort_order"]
    genre_filter = query_data["genre_filter"]

    query_parameters = f"?sort={sort_order}&genre_id={genre_filter}"

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
async def test_cache_film_by_id(redis_client, make_get_request):

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

    assert response.status == 200
    assert body["uuid"] == film_id
    assert body["title"] == "CACHE"

    await redis_client.delete(key)

    response = await make_get_request(test_settings.ES_FILM_IDX, film_id)
    assert response.status == 404

from typing import Dict
from uuid import uuid4
import pickle
import pytest
from db.redis import form_key
from models.genre import Genre
from tests.functional.settings import test_settings



@pytest.mark.parametrize(
    "query_data, exp_answer",
    [
        (
            "3d8d9bf5-0d90-4353-88ba-4ccc5d2c07ff",
            {"status": 200, "name": "Action"},
        ),
        (
            "qwea21cf-9097-479e-904a-13dd7198c1dd",
            {"status": 404, "name": None},
        ),
        (
            "INCORRECT-UUID-FORMAT",
            {"status": 404, "name": None},
        ),
    ],
)
@pytest.mark.asyncio
async def test_search_genre_by_id(
    make_get_request, query_data: str, exp_answer: Dict
):

    response = await make_get_request(test_settings.ES_GENRE_IDX, query_data)

    body = await response.json()
    status = response.status

    assert status == exp_answer.get("status")
    assert body.get("name") == exp_answer.get("name")


@pytest.mark.asyncio
async def test_list_genres(make_get_request):

    response = await make_get_request(test_settings.ES_GENRE_IDX, "")

    body = await response.json()
    status = response.status

    assert len(body) == 26
    assert status == 200


@pytest.mark.parametrize(
    "query_data, exp_answer",
    [
        (
            {"page_size": 30, "page_number": 1},
            {"status": 200, "body_len": 26},
        ),
        (
            {"page_size": 10, "page_number": 1},
            {"status": 200, "body_len": 10},
        ),
        (
            {"page_size": 10, "page_number": 2},
            {"status": 200, "body_len": 10},
        ),
        (
            {"page_size": 10, "page_number": 3},
            {"status": 200, "body_len": 6},
        ),
        (
            {"page_size": 10, "page_number": 4},
            {"status": 400, "body_len": 1},
        ),
        (
            {"page_size": 51, "page_number": 1},
            {"status": 422, "body_len": 1},
        ),
    ],
)
@pytest.mark.asyncio
async def test_list_genres_with_pages(
    make_get_request, query_data: Dict, exp_answer: Dict
):

    page_size = query_data['page_size']
    page_number = query_data['page_number']

    query_parameters = f"?page_size={page_size}&page_number={page_number}"

    response = await make_get_request(test_settings.ES_GENRE_IDX, query_parameters)

    body = await response.json()
    status = response.status

    assert status == exp_answer.get("status")
    assert len(body) == exp_answer.get("body_len")


@pytest.mark.asyncio
async def test_cache_genre_by_id(redis_client, make_get_request):

    genre_id = str(uuid4())
    key = form_key("get_by_id", (genre_id,), {})
    test_genre_data = Genre(id=genre_id, name="CACHE")

    await redis_client.set(key, pickle.dumps(test_genre_data), ex=60)

    response = await make_get_request(test_settings.ES_GENRE_IDX, genre_id)
    body = await response.json()

    assert response.status == 200
    assert body["uuid"] == genre_id
    assert body["name"] == "CACHE"

    await redis_client.delete(key)

    response = await make_get_request(test_settings.ES_GENRE_IDX, genre_id)
    assert response.status == 404

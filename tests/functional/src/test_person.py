from typing import Dict
from uuid import uuid4
import pickle
import pytest

from db.redis import form_key
from models.person import Person
from tests.functional.settings import test_settings


@pytest.mark.parametrize(
    "query_data, exp_answer",
    [
        (
            "a5a8f573-3cee-4ccc-8a2b-91cb9f55250a",
            {"status": 200, "name": "George Lucas"},
        ),
        (
            "a5a8f513-3c7e-4vcc-8a2b-91cbff55250a",
            {"status": 404, "name": None},
        ),
        (
            "",
            {"status": 404, "name": None},
        ),
    ],
)
@pytest.mark.asyncio
async def test_search_person_by_id(
    make_get_request, query_data: str, exp_answer: Dict
):

    response = await make_get_request(test_settings.ES_PERSON_IDX, query_data)

    body = await response.json()
    status = response.status

    assert status == exp_answer.get("status")
    assert body.get("full_name") == exp_answer.get("name")


@pytest.mark.asyncio
async def test_cache_person_by_id(redis_client, make_get_request):
    person_id = str(uuid4())
    key = form_key("get_by_id", (person_id,), {})
    test_person_data = Person(id=person_id, full_name="CACHE", films=[])

    await redis_client.set(key, pickle.dumps(test_person_data), ex=60)

    response = await make_get_request(test_settings.ES_PERSON_IDX, person_id)
    body = await response.json()

    assert response.status == 200
    assert body["uuid"] == person_id
    assert body["full_name"] == "CACHE"

    await redis_client.delete(key)

    response = await make_get_request(test_settings.ES_PERSON_IDX, person_id)
    assert response.status == 404

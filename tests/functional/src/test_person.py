from typing import Dict

import pytest
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

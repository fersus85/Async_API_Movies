from typing import Dict

import pytest


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
    ],
)
@pytest.mark.asyncio
async def test_search_genre_by_id(
    make_get_request, query_data: str, exp_answer: Dict
):

    response = await make_get_request("genres", query_data)

    body = await response.json()
    status = response.status

    assert status == exp_answer.get("status")
    assert body.get("name") == exp_answer.get("name")


@pytest.mark.asyncio
async def test_list_genres(make_get_request):

    response = await make_get_request("genres", "")

    body = await response.json()
    status = response.status

    assert len(body) == 26
    assert status == 200

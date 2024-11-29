from typing import Dict, Any, Callable, List
from urllib.parse import urlencode
from uuid import uuid4

import pytest
from aiohttp import ClientResponse
from pydantic import BaseModel
from redis.asyncio import Redis

from db.redis import form_key, RedisCache
from schemas.film import FilmSchema
from schemas.person import PersonSchema
from models.film import Film
from models.person import Person
from tests.functional.settings import test_settings
from tests.functional.utils.helpers import perform_request_and_assert, \
    multi_word_check


@pytest.mark.parametrize(
    "query_data, exp_answer",
    [
        pytest.param(
            {"query": "empt", "page_size": -1, "page_number": 1},
            {"status": 422, "body_len": 1},
            id="incorrect page_size"
        ),
        pytest.param(
            {"query": "empt", "page_size": 30, "page_number": 0},
            {"status": 422, "body_len": 1},
            id="incorrect page_number"
        ),
        pytest.param(
            {"query": "empt", "page_size": 0, "page_number": 0},
            {"status": 422, "body_len": 1},
            id="incorrect page_size and page_number"
        ),
        pytest.param(
            {"query": "empt", "page_size": 30, "page_number": 10000000},
            {"status": 400, "body_len": 1},
            id="exceed max pages"
        ),
        pytest.param(
            {"page_size": 30, "page_number": 1},
            {"status": 422, "body_len": 1},
            id="missing query"
        ),
        pytest.param(
            {"query": "", "page_size": 30, "page_number": 1},
            {"status": 200, "body_len": 0},
            id="empty query"
        ),
        pytest.param(
            {"query": "empt", "page_size": "abc", "page_number": 1},
            {"status": 422, "body_len": 1},
            id="invalid page_size type"
        ),
        pytest.param(
            {"query": "empt", "page_size": 30, "page_number": "abc"},
            {"status": 422, "body_len": 1},
            id="invalid page_number type"
        ),
        pytest.param(
            {"query": "empt", "page_size": 10000, "page_number": 1},
            {"status": 422, "body_len": 1},
            id="exceed max page_size"
        ),
        pytest.param(
            {},
            {"status": 422, "body_len": 1},
            id="no all params"
        ),
    ],
)
@pytest.mark.asyncio
async def test_invalid_params(
        make_get_request: Callable[[str, str], ClientResponse],
        query_data: Dict[str, Any],
        exp_answer: Dict[str, Any]
):
    """
    Test function for validating the handling of
    invalid query parameters in API requests.

    Parameters:
    - make_get_request: Fixture to make GET requests to the API endpoint.
    - query_data: Dictionary containing the query parameters
        to be used in the API request.
    - exp_answer: Dictionary containing the expected
        response from the API, which includes the expected HTTP
        status code and the length of the response body.

    Actions:
    - Iterates over indices (films and persons) and
        performs a GET request to the '/search' endpoint.
    - Asserts that the response status and body length against expected values.
    """
    for index in (test_settings.ES_FILM_IDX, test_settings.ES_PERSON_IDX):
        await perform_request_and_assert(
            make_get_request, query_data, exp_answer, index
        )


@pytest.mark.parametrize(
    "query_data, exp_answer",
    [
        pytest.param(
            {"query": "Star", "page_size": 30, "page_number": 1},
            {"status": 200, "body_len": 6},
            id="correct page_size and page_number"
        ),
        pytest.param(
            {"query": "Star", "page_size": 2, "page_number": 1},
            {"status": 200, "body_len": 2},
            id="correct small page"
        ),
        pytest.param(
            {"query": "Star", "page_size": 5, "page_number": 2},
            {"status": 200, "body_len": 1},
            id="correct last page"
        ),
        pytest.param(
            {"query": "UNEXISTS", "page_size": 30, "page_number": 1},
            {"status": 200, "body_len": 0},
            id="non-exists query result"
        ),
        pytest.param(
            {"query": "Star", "page_size": 1, "page_number": 1},
            {"status": 200, "body_len": 1},
            id="min page_size and page_number"
        ),
        pytest.param(
            {"query": "Star"},
            {"status": 200, "body_len": 6},
            id="no page_size and page_number"
        ),
        pytest.param(
            {"query": " Star%", "page_size": 20, "page_number": 1},
            {"status": 200, "body_len": 6},
            id="query with special chars"
        ),
        pytest.param(
            {"query": "a" * 1000000, "page_size": 30, "page_number": 1},
            {"status": 200, "body_len": 0},
            id="big query"
        ),
    ],
)
@pytest.mark.asyncio
async def test_film_search_simple(
        make_get_request: Callable[[str, str], ClientResponse],
        query_data: Dict[str, Any],
        exp_answer: Dict[str, Any]
):
    """
    Test function for verifying correct handling of valid
    query parameters in "film" search requests to the '/search' endpoint.

    Parameters:
    - make_get_request: Fixture to make GET requests to the API endpoint.
    - query_data: Dictionary containing the query parameters
        to be used in the API request.
    - exp_answer: Dictionary containing the expected
        response from the API, which includes the expected HTTP
        status code and the length of the response body.

    Actions:
    - Performs a GET request to the '/search' endpoint for films
        with the given query parameters.
    - Asserts that the response status and body length against expected values.
    """
    await perform_request_and_assert(
        make_get_request, query_data, exp_answer, test_settings.ES_FILM_IDX
    )


@pytest.mark.parametrize(
    "query_data, exp_answer",
    [
        pytest.param(
            {"query": "Ivan", "page_size": 30, "page_number": 1},
            {"status": 200, "body_len": 0},
            id="correct page_size and page_number"
        ),
        pytest.param(
            {"query": "Endô", "page_size": 50, "page_number": 1},
            {"status": 200, "body_len": 1},
            id="non ascii"
        ),
    ],
)
@pytest.mark.asyncio
async def test_person_search_simple(
        make_get_request: Callable[[str, str], ClientResponse],
        query_data: Dict[str, Any],
        exp_answer: Dict[str, Any]
):
    """
    Test function for verifying correct handling of valid
    query parameters in "person" search requests to the '/search' endpoint.

    Parameters:
    - make_get_request: Fixture to make GET requests to the API endpoint.
    - query_data: Dictionary containing the query parameters
        to be used in the API request.
    - exp_answer: Dictionary containing the expected
        response from the API, which includes the expected HTTP
        status code and the length of the response body.

    Actions:
    - Performs a GET request to the '/search' endpoint for persons
        with the given query parameters.
    - Asserts that the response status and body length against expected values.
    """
    await perform_request_and_assert(
        make_get_request, query_data, exp_answer, test_settings.ES_PERSON_IDX
    )


@pytest.mark.parametrize(
    "query_data, predicate",
    [
        pytest.param(
            {"query": "Star", "page_size": 30, "page_number": 1},
            lambda query, response: all(query.lower() in row["title"].lower()
                                        for row in response),
            id="simple query"
        ),
        pytest.param(
            {"query": "sTAr", "page_size": 30, "page_number": 1},
            lambda query, response: all(query.lower() in row["title"].lower()
                                        for row in response),
            id="case insensitive query"
        ),
        pytest.param(
            {"query": "Lucky Wars", "page_size": 10, "page_number": 1},
            multi_word_check,
            id="multi word query"
        ),
    ]
)
@pytest.mark.asyncio
async def test_film_search_predicate(
        make_get_request: Callable[[str, str], ClientResponse],
        query_data: Dict[str, Any],
        predicate: Callable[[str, List[Dict[str, str]]], bool]
):
    """
    Test function for checking the content of film search
    results matches expected conditions.

    Parameters:
    - make_get_request: Fixture to make GET requests to the API endpoint.
    - query_data: Dictionary containing the query parameters
        to be used in the API request.
    - predicate (Callable[[str, List[Dict[str, str]]], bool]):
    Function that evaluates whether the response meets
    the expected condition based on the query.

    Actions:
    - Performs a GET request to the '/search' endpoint for films
        with the given query parameters.
    - Applies the predicate to the response body to validate the content.
    - Asserts that the predicate returns True.
    """
    query_parameters = f"?{urlencode(query_data)}"

    response = await make_get_request(
        test_settings.ES_FILM_IDX, 'search' + query_parameters
    )

    body = await response.json()

    assert predicate(query_data.get("query"), body) is True


@pytest.mark.parametrize(
    "fake_data, query_data, exp_answer, index",
    [
        pytest.param(
            [
                Film(id=uuid4(), title="!Super-Star!", directors=[], actors=[],
                     writers=[], genres=[])
            ],
            {"query": "Star", "page_size": 30, "page_number": 1},
            {"status": 200, "body_len": 1},
            test_settings.ES_FILM_IDX,
            id="cache films"
        ),
        pytest.param(
            [
                Person(id=uuid4(), full_name="Harrison Toyota", films=[]),
                Person(id=uuid4(), full_name="Toyota Corolla", films=[])
            ],
            {"query": "Toyota", "page_size": 30, "page_number": 1},
            {"status": 200, "body_len": 2},
            test_settings.ES_PERSON_IDX,
            id="cache persons"
        ),
    ]
)
@pytest.mark.asyncio
async def test_cache(
        make_get_request: Callable[[str, str], ClientResponse],
        redis_client: Redis,
        fake_data: List[BaseModel],
        query_data: Dict[str, Any],
        exp_answer: Dict[str, Any],
        index: str
):
    """
    Test function for verifying the caching mechanism for search
    results to the '/search' endpoint.

    Parameters:
    - make_get_request (Callable[[str, str], ClientResponse]):
        Fixture to make GET requests to the API endpoint.
    - redis_client (Redis): Redis client for interacting with the cache.
    - fake_data (List[BaseModel]): List of fake data objects to be cached.
    - query_data (Dict[str, Any]):
        Dictionary containing the query parameters to
        be used in the API request.
    - exp_answer (Dict[str, Any]):
        Dictionary containing the expected response from the API,
        including the expected HTTP status code and the length of
        the response body.
    - index (str):
        The index or base URL for making the request
        (e.g., film or person index).

    Actions:
    - Forms a cache key based on the query parameters.
    - Stores the fake data in the cache under the formed key.
    - Performs a GET request to the '/search'
        endpoint with the given query parameters.
    - Asserts that the response status and body length against expected values.
    - Deletes the cache entry after the test.
    """
    redis_cache = RedisCache(redis_client)

    key = form_key("search",
                   (query_data["query"],
                    query_data["page_size"],
                    query_data["page_number"]),
                   {})

    await redis_cache.set(key, fake_data, 60)

    await perform_request_and_assert(
        make_get_request, query_data, exp_answer, index
    )

    await redis_cache.cacher.delete(key)


@pytest.mark.parametrize(
    "query_data, index, valid_schema",
    [
        pytest.param(
            {"query": "Star"},
            test_settings.ES_FILM_IDX,
            FilmSchema,
            id="film schema"
        ),
        pytest.param(
            {"query": "Aya"},
            test_settings.ES_PERSON_IDX,
            PersonSchema,
            id="person schema"
        ),
    ]
)
@pytest.mark.asyncio
async def test_structure(
        make_get_request: Callable[[str, str], ClientResponse],
        query_data: Dict[str, Any],
        index: str,
        valid_schema: BaseModel
):
    """
    Test function for validating the structure of the search
    results against a given schema when accessing the '/search' endpoint.

    Parameters:
    - make_get_request: Fixture to make GET requests to the API endpoint.
    - query_data: Dictionary containing the query parameters
        to be used in the API request.
    - index (str): The index or base URL for making the request
        (e.g., film or person index).
    - valid_schema (BaseModel): The Pydantic model used to validate
        the structure of each item in the response.

    Actions:
    - Performs a GET request to the '/search'
        endpoint with the given query parameters.
    - Validates each item in the response body against the provided schema.
    - Asserts that each item conforms to the expected structure
    """
    query_parameters = f"?{urlencode(query_data)}"

    response = await make_get_request(
        index, 'search' + query_parameters
    )

    body = await response.json()

    for row in body:
        valid_schema.model_validate(row)

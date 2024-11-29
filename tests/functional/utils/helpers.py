from typing import Callable, Any, Dict, List
from urllib.parse import urlencode

from aiohttp import ClientResponse


async def perform_request_and_assert(
        make_get_request: Callable[[str, str], ClientResponse],
        query_data: Dict[str, Any],
        exp_answer: Dict[str, Any],
        index: str
):
    """
    Performs a GET request to the '/search' endpoint
    and validates the response against expected values.

    Parameters:
        make_get_request (Callable[[str, str], ClientResponse]):
            Function to perform the GET request.
        query_data (Dict[str, Any]):
            Query parameters as a dictionary.
        exp_answer (Dict[str, Any]):
            Expected response containing 'status' and 'body_len'.
        index (str):
            Index for making the request.
    """
    query_parameters = f"?{urlencode(query_data)}"

    response = await make_get_request(
        index, 'search' + query_parameters
    )

    body = await response.json()
    status = response.status

    assert status == exp_answer.get("status")
    assert len(body) == exp_answer.get("body_len")


def multi_word_check(
        query: str,
        response: List[Dict[str, str]],
        field: str = "title"
) -> bool:
    """
    Checks if the specified field in each item of
    the response contains at least one word from the query.

    Parameters:
        query (str):
            Query string containing one or more words.
        response (List[Dict[str, str]]):
            List of dictionaries containing the specified field.
        field (str):
            The key of the field to be checked in each dictionary.
    """
    for row in response:
        value = row.get(field)
        if not any(split.lower() in value.lower()
                   for split in str(query).split(' ')):
            return False

    return True

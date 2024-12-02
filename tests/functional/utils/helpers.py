import asyncio
import logging
from random import normalvariate
from functools import wraps
from typing import Callable, Any, Dict, List, TypeVar
from urllib.parse import urlencode

from aiohttp import ClientResponse


logger = logging.getLogger(__name__)


async def perform_request_and_assert(
    make_get_request: Callable[[str, str], ClientResponse],
    query_data: Dict[str, Any],
    exp_answer: Dict[str, Any],
    index: str,
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

    response = await make_get_request(index, "search" + query_parameters)

    body = await response.json()
    status = response.status

    assert status == exp_answer.get("status")
    assert len(body) == exp_answer.get("body_len")


def multi_word_check(
    query: str, response: List[Dict[str, str]], field: str = "title"
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
        if not any(
            split.lower() in value.lower() for split in str(query).split(" ")
        ):
            return False

    return True


F = TypeVar("F", bound=Callable[..., Any])


def backoff(
    start_sleep_time: float = 0.1,
    factor: int = 2,
    border_sleep_time: int = 10,
    jitter: float = 0.1,
    max_tries: int = 15,
) -> Callable[[F], F]:
    """
    Функция для повторного выполнения функции через некоторое время,
    если возникла ошибка. Использует наивный экспоненциальный рост времени
    повтора (factor) до граничного времени ожидания (border_sleep_time)

    Формула:
        t = start_sleep_time * (factor ^ n), если t < border_sleep_time
        t = border_sleep_time, иначе
    :param start_sleep_time: начальное время ожидания
    :param factor: во сколько раз нужно увеличивать ожиданиe на каждой итерации
    :param border_sleep_time: максимальное время ожидания
    :param jitter: случайное время ожидания для уменьшения пиков нагрузки
    :max_tries: максимальное кол-во попыток подключения
    :return: результат выполнения функции
    """

    def func_wrapper(func: F) -> F:
        @wraps(func)
        async def inner(*args: Any, **kwargs: Any) -> Any:
            delay = start_sleep_time
            tries = 0
            while tries < max_tries:
                try:
                    flag = await func(*args, **kwargs)
                    if flag:
                        return flag
                except Exception as ex:
                    logger.error("Произошла ошибка ожидания сервиса: %s", ex)

                tries += 1
                jit_time = normalvariate(0, delay * jitter)
                sleep_time = min(delay + jit_time, border_sleep_time)
                delay = min(delay * factor, border_sleep_time)

                await asyncio.sleep(sleep_time)

                if tries == max_tries:
                    logger.error("Достигнуто максимальное кол-во попыток")
                    break
            return False

        return inner

    return func_wrapper

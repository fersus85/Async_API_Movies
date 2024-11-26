import asyncio
from typing import Optional, Callable, AsyncGenerator, Dict, Any, List
from uuid import uuid4

import aiohttp
import pytest_asyncio
from elasticsearch import AsyncElasticsearch
from redis.asyncio import Redis

from tests.functional.settings import test_settings
from models.film import FilmShort


@pytest_asyncio.fixture(scope="session")
def event_loop():
    """
    Фикстура, предоставляющая цикл событий asyncio для сессии тестирования.

    Возвращает:
        asyncio.AbstractEventLoop: Цикл событий для использования в тестах.
    """
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(name="aiohttp_client", scope="session")
async def aiohttp_client() -> AsyncGenerator[aiohttp.ClientSession, None]:
    """
    Фикстура, создающая и управляющая сессией aiohttp ClientSession.

    Используется для выполнения HTTP-запросов в тестах.

    Возвращает:
        AsyncGenerator[aiohttp.ClientSession, None]: Асинхронный генератор,
        который предоставляет сессию aiohttp для выполнения запросов.
    """
    session = aiohttp.ClientSession()
    yield session
    await session.close()


@pytest_asyncio.fixture(name="es_client", scope="session")
async def es_client() -> AsyncGenerator[AsyncElasticsearch, None]:
    """
    Фикстура, создающая асинхронный клиент Elasticsearch.

    Используется для взаимодействия с Elasticsearch в тестах.

    Возвращает:
        AsyncGenerator[AsyncElasticsearch, None]: Асинхронный генератор,
        который предоставляет клиент Elasticsearch для выполнения
        операций с индексами и документами.
    """
    es_client = AsyncElasticsearch(
        hosts=f"http://{test_settings.ES_HOST}:{test_settings.ES_PORT}",
        verify_certs=False,
    )
    yield es_client
    await es_client.close()


@pytest_asyncio.fixture(name="redis_client", scope="session")
async def redis_client() -> AsyncGenerator[Redis, None]:
    """
    Фикстура, создающая клиент Redis.

    Используется для взаимодействия с Redis в тестах.
    В зависимости от URL сервиса клиент может подключаться к
    локальному или удаленному Redis.

    Возвращает:
        AsyncGenerator[Redis, None]: Асинхронный генератор,
        который предоставляет клиент Redis для выполнения операций с данными.
    """

    if test_settings.SERVICE_URL == "http://localhost:8000":
        client = Redis(host="localhost", port=test_settings.REDIS_PORT)
        yield client
        await client.aclose()
    else:
        client = Redis(host="redis", port=test_settings.REDIS_PORT)
        yield client
        await client.aclose()


@pytest_asyncio.fixture(name="es_write_data")
def es_write_data(
    es_client: AsyncElasticsearch,
) -> Callable[[Dict[str, Any]], None]:
    """
    Фикстура, предоставляющая функцию для записи данных в Elasticsearch.

    Используется для создания или удаления индексов и добавления документов
    в Elasticsearch в процессе тестирования.

    Параметры:
        es_client (AsyncElasticsearch): Клиент Elasticsearch.

    Возвращает:
        Callable[[Dict[str, Any]], None]: Функция, принимающая словарь
        с данными для записи в Elasticsearch.
    """

    async def inner(data: Dict[str, Any]) -> None:
        idx = data["index"]
        if await es_client.indices.exists(index=idx):
            await es_client.indices.delete(index=idx)
        await es_client.indices.create(index=idx, mappings=data["mapping"])

        obj_id = data.get("object_id")
        obj_data = data.get("object_data")
        await es_client.index(index=idx, id=obj_id, document=obj_data)

    return inner


@pytest_asyncio.fixture(name="make_get_request")
def make_get_request(
    aiohttp_client: aiohttp.ClientSession,
) -> Callable[[str, str], aiohttp.ClientResponse]:
    """
    Фикстура, предоставляющая функцию для выполнения GET-запросов к сервису.

    Используется для выполнения GET-запросов к API.

    Параметры:
        aiohttp_client (aiohttp.ClientSession): Сессия aiohttp.

    Возвращает:
        Callable[[str, str], aiohttp.ClientResponse]: Функция,
        принимающая имя сервиса и данные для запроса,
        возвращающая ответ от сервиса.
    """
    async def inner(service: str, data: str) -> aiohttp.ClientResponse:
        url = test_settings.SERVICE_URL + f"/api/v1/{service}s/{data}"
        response = await aiohttp_client.get(url)
        return response

    return inner


@pytest_asyncio.fixture(name="make_request_persons_list")
def make_request_persons_list(
    aiohttp_client: aiohttp.ClientSession,
) -> Callable[[str, str, Optional[str]], aiohttp.ClientResponse]:
    """
    Фикстура, предоставляющая функцию для выполнения GET-запросов.

    Используется для получения информации о фильмах, связанных с персоной

    Параметры:
        aiohttp_client (aiohttp.ClientSession): Сессия aiohttp.

    Возвращает:
        Callable[[str, str, Optional[str]], aiohttp.ClientResponse]: Функция,
        принимающая имя сервиса, идентификатор элемента и необязательные
        параметры запроса, возвращающая ответ от сервиса в виде
        объекта aiohttp.ClientResponse.
    """

    async def inner(
        service: str, item_id: str, params: Optional[str] = None
    ) -> aiohttp.ClientResponse:
        url = test_settings.SERVICE_URL + f"/api/v1/{service}s/{item_id}/film"
        if params:
            url += params
        response = await aiohttp_client.get(url)
        return response

    return inner


@pytest_asyncio.fixture(name="get_short_list")
async def get_short_list() -> List[FilmShort]:
    """
    Асинхронная фикстура, возвращающая список объектов FilmShort.

    Используется для создания тестовых данных, представляющих фильмы с их
    идентификаторами, названиями и рейтингами IMDb.

    Возвращает:
        List[FilmShort]: Список объектов FilmShort, содержащих тестовые данные
        о фильмах.
    """
    person_list = [
        {"f_id": uuid4(), "title": "Fool", "imdb_rating": 7.0},
        {"f_id": uuid4(), "title": "Fool2", "imdb_rating": 7.0},
    ]
    return [
        FilmShort(
            uuid=item["f_id"],
            title=item["title"],
            imdb_rating=item["imdb_rating"],
        )
        for item in person_list
    ]

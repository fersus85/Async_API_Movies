import pytest_asyncio
import asyncio

from elasticsearch import AsyncElasticsearch
from redis.asyncio import Redis
import aiohttp

from tests.functional.settings import test_settings


@pytest_asyncio.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(name="aiohttp_client", scope="session")
async def aiohttp_client():
    session = aiohttp.ClientSession()
    yield session
    await session.close()


@pytest_asyncio.fixture(name="es_client", scope="session")
async def es_client():
    es_client = AsyncElasticsearch(
        hosts=f"http://{test_settings.ES_HOST}:{test_settings.ES_PORT}",
        verify_certs=False,
    )
    yield es_client
    await es_client.close()


@pytest_asyncio.fixture(name="redis_client", scope="session")
async def redis_client():
    if test_settings.SERVICE_URL == "http://localhost:8000":
        client = Redis(host="localhost", port=test_settings.REDIS_PORT)
        yield client
        await client.aclose()
    else:
        client = Redis(host="redis", port=test_settings.REDIS_PORT)
        yield client
        await client.aclose()


@pytest_asyncio.fixture(name="es_write_data")
def es_write_data(es_client: AsyncElasticsearch):
    async def inner(data: dict):
        idx = data["index"]
        if await es_client.indices.exists(index=idx):
            await es_client.indices.delete(index=idx)
        await es_client.indices.create(index=idx, mappings=data["mapping"])

        obj_id = data.get("object_id")
        obj_data = data.get("object_data")
        await es_client.index(index=idx, id=obj_id, document=obj_data)

    return inner


@pytest_asyncio.fixture(name="make_get_request")
def make_get_request(aiohttp_client: aiohttp.ClientSession):
    async def inner(service: str, data: str):
        url = test_settings.SERVICE_URL + f"/api/v1/{service}s/{data}"
        response = await aiohttp_client.get(url)
        return response

    return inner

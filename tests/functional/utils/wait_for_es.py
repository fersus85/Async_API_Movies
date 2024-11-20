import asyncio

from elasticsearch import AsyncElasticsearch
from tests.functional.settings import test_settings


async def wait_for_es(es_client: AsyncElasticsearch):
    while True:
        if await es_client.ping():
            print("Elasticsearch is ready!")
            break
        await asyncio.sleep(1)


async def main():
    es_client = AsyncElasticsearch(
        hosts=[
            f'http://{test_settings.ES_HOST}:{test_settings.ES_PORT}'
            ]
        )
    try:
        await wait_for_es(es_client)
    finally:
        await es_client.close()

if __name__ == '__main__':
    asyncio.run(main())

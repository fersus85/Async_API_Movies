import asyncio
import logging

from elasticsearch import AsyncElasticsearch
from tests.functional.settings import test_settings
from helpers import backoff


logger = logging.getLogger(__name__)


@backoff()
async def wait_for_es(es_client: AsyncElasticsearch) -> bool:
    """
    Проверяет доступность сервиса Elasticsearch.

    Выполняет ping к Elasticsearch и возвращает True, если сервис доступен,
    иначе возвращает False. Логирует информацию о состоянии сервиса.

    :param es_client: Асинхронный клиент Elasticsearch.
    :return: True, если Elasticsearch доступен, иначе False.
    """
    if await es_client.ping():
        logger.info("Elasticsearch is ready!")
        return True
    logger.warning("Elasticsearch is not ready yet.")
    return False


async def main() -> None:
    """
    Основная функция, которая инициализирует клиент Elasticsearch
    и ожидает его доступности с помощью функции wait_for_es.
    Логирует ошибки, если подключение не удалось.
    """
    es_client = AsyncElasticsearch(
        hosts=[f"http://{test_settings.ES_HOST}:{test_settings.ES_PORT}"]
    )
    try:
        result = await wait_for_es(es_client)
        if not result:
            logger.error("Failed to connect to Elasticsearch")
    except Exception as e:
        logger.error("An error occurred while waiting Elasticsearch: %s", e)
    finally:
        await es_client.close()


if __name__ == "__main__":
    asyncio.run(main())

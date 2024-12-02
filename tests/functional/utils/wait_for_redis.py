import asyncio
import logging

from redis.asyncio import Redis

from tests.functional.settings import test_settings
from helpers import backoff


logger = logging.getLogger(__name__)


@backoff()
async def wait_for_redis(redis: Redis) -> bool:
    """
    Проверяет доступность сервиса Redis.

    Выполняет ping к Redis и возвращает True, если сервис доступен,
    иначе возвращает False. Логирует информацию о состоянии сервиса.

    :param redis: Асинхронный клиент Redis.
    :return: True, если Redis доступен, иначе False.
    """
    if await redis.ping():
        logger.info("Redis is ready!")
        return True
    logger.warning("Redis is not ready yet.")
    return False


async def main() -> None:
    """
    Основная функция, которая инициализирует клиент Redis
    и ожидает его доступности с помощью функции wait_for_redis.
    Логирует ошибки, если подключение не удалось.
    """
    redis_client = Redis(
        host=test_settings.REDIS_HOST, port=test_settings.REDIS_PORT
    )
    try:
        result = await wait_for_redis(redis_client)
        if not result:
            logger.error("Failed to connect to Redis")
    except Exception as e:
        logger.error("An error occurred while waiting Redis: %s", e)
    finally:
        await redis_client.aclose()


if __name__ == "__main__":
    asyncio.run(main())

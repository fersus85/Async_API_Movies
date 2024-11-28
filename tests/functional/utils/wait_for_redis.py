import asyncio
import logging

from redis.asyncio import Redis
from tests.functional.settings import test_settings


logger = logging.getLogger(__name__)


async def wait_for_redis(redis: Redis):
    while True:
        if await redis.ping():
            logger.info("Redis is ready!")
            break
        await asyncio.sleep(1)


async def main():
    redis_client = Redis(
        host=test_settings.REDIS_HOST, port=test_settings.REDIS_PORT
    )
    try:
        await wait_for_redis(redis_client)
    finally:
        await redis_client.aclose()


if __name__ == "__main__":
    asyncio.run(main())

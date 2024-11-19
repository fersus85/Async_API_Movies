import time

from from redis.asyncio import Redis
from functional.settings import  settings


if __name__ == '__main__':
    redis_client = Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)
    while True:
        if redis_client.ping():
            break
        time.sleep(1)

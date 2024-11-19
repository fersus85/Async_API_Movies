import logging
import pickle
from functools import wraps
from hashlib import sha256
from typing import Optional, Callable
from redis.asyncio import Redis

redis: Optional[Redis] = None

logger = logging.getLogger(__name__)


# Функция понадобится при внедрении зависимостей
async def get_redis() -> Redis:
    return redis


def form_key(*args, **kwargs) -> str:
    return sha256(pickle.dumps((args, kwargs))).hexdigest()


def redis_cache_method(redis_attr: str, expire: int = 1800):
    """
    redis_cache_method is a decorator that caches the result of an asynchronous method in a Redis store.

    Parameters:
    - redis_attr (str): The attribute name for the Redis instance in the class.
    - expire (int): The cache expiration time in seconds. Defaults to 1800 seconds (30 minutes).

    Raises:
    - ValueError: If the Redis instance is not set or not of the correct type.
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            redis_ = getattr(self, redis_attr, None)
            if redis_ is None or not isinstance(redis_, Redis):
                raise ValueError('Redis instance is not set')

            key = form_key(func.__name__, args, kwargs)

            cache = await redis_.get(key)
            if cache is not None:
                logger.debug('Response from cache')
                return pickle.loads(cache)

            result = await func(self, *args, **kwargs)
            await redis_.set(key, pickle.dumps(result), ex=expire)
            logger.debug('Response from ES')
            return result

        return wrapper

    return decorator

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from core.config import settings
from core.log_config import setup_logging

from elasticsearch import AsyncElasticsearch
from redis.asyncio import Redis

import db.searcher as searcher
import db.cacher as cacher
from db import elastic
from db import redis
from db.searcher.elastic_searcher import ElasticSearchEngine
from api.v1 import films
from api.v1 import genres
from api.v1 import persons
from db.redis import RedisCache

setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis.redis = Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)
    cacher.cacher = RedisCache(redis.redis)
    elastic.es_client = AsyncElasticsearch(
        hosts=[f'http://{settings.ELASTIC_HOST}:{settings.ELASTIC_PORT}']
        )
    searcher.search_engine = ElasticSearchEngine(elastic.es_client)
    logger.debug('Successfully connected to Redis and Elasticsearch.')
    yield
    logger.debug("Closing connections")
    await redis.redis.close()
    await elastic.es_client.close()


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="AsyncAPI movies services",
    version="1.0.0",
    lifespan=lifespan,
    root_path="/api",
    docs_url="/openapi",
    openapi_url="/openapi.json",
    default_response_class=ORJSONResponse,
)

app.include_router(films.router, prefix="/v1/films", tags=["film_service"])
app.include_router(genres.router, prefix="/v1/genres", tags=["genre_service"])
app.include_router(
    persons.router, prefix="/v1/persons", tags=["person_service"]
)

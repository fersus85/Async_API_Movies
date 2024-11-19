import time

from elasticsearch import AsyncElasticsearch
from functional.settings import  settings

if __name__ == '__main__':
    es_client = AsyncElasticsearch(
        hosts=[f'http://{settings.ELASTIC_HOST}:{settings.ELASTIC_PORT}']
        )
    while True:
        if es_client.ping():
            break
        time.sleep(1)

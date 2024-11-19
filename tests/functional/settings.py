from pydantic_settings import BaseSettings, SettingsConfigDict


class TestSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='test.env',
        env_ignore_empty=True,
        extra='ignore'
    )
    ES_INDEX: str = 'test'
    ES_ID_FIELD: str = ''
    ES_INDEX_MAPPING: dict = ''
    SERVICE_URL: str = 'tests'

    ELASTIC_HOST: str = '127.0.0.1'
    ELASTIC_PORT: int = 9200

    REDIS_HOST: str = '127.0.0.1'
    REDIS_PORT: int = 6379


settings = TestSettings()

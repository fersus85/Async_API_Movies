from pydantic_settings import BaseSettings, SettingsConfigDict


class TestSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_ignore_empty=True, extra="ignore"
    )
    ES_PERSON_IDX: str = "person"
    ES_FILM_IDX: str = "film"
    ES_GENRE_IDX: str = "genre"

    SERVICE_URL: str = "http://fastapi:8000"

    ES_HOST: str = "elastic"
    ES_PORT: int = 9200

    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379


test_settings = TestSettings()

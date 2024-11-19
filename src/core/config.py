import os

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env',
        env_ignore_empty=True,
        extra='ignore'
    )
    PROJECT_NAME: str = 'movies'
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    ELASTIC_HOST: str = '127.0.0.1'
    ELASTIC_PORT: int = 9200

    REDIS_HOST: str = '127.0.0.1'
    REDIS_PORT: int = 6379


settings = Settings()

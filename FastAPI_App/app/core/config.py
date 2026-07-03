from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = ConfigDict(env_file=".env")

    database_url: str = (
        "postgresql+asyncpg://postgres:postgres@localhost:5432/docprocessor"
    )
    test_database_url: str = (
        "postgresql+asyncpg://postgres:postgres@localhost:5432/docprocessor_test"
    )
    temporal_host: str = "localhost:7233"


settings = Settings()

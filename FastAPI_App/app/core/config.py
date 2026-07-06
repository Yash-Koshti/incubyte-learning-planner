from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = ConfigDict(env_file=".env")

    database_url: str = (
        "postgresql+asyncpg://postgres:postgres@localhost:5432/docprocessor"
    )


settings = Settings()

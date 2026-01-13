from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    GALAXY_TIME_FORMAT: str = "%Y-%m-%dT%H:%M:%S.%f"


settings = Settings()

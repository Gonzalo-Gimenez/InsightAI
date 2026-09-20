from urllib.parse import urlparse

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    GROQ_API_KEY: str
    GROQ_MODEL: str

    DATABASE_URL: str | None = None

    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5433
    POSTGRES_DB: str = "insight_ai"
    POSTGRES_USER: str = "insight_ai"
    POSTGRES_PASSWORD: str = ""

    @model_validator(mode="after")
    def apply_database_url(self):
        if not self.DATABASE_URL:
            return self
        parsed = urlparse(self.DATABASE_URL)
        if parsed.hostname:
            self.POSTGRES_HOST = parsed.hostname
        if parsed.port:
            self.POSTGRES_PORT = parsed.port
        if parsed.path and len(parsed.path) > 1:
            self.POSTGRES_DB = parsed.path.lstrip("/")
        if parsed.username:
            self.POSTGRES_USER = parsed.username
        if parsed.password:
            self.POSTGRES_PASSWORD = parsed.password
        return self


settings = Settings()

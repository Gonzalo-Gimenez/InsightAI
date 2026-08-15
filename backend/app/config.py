from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    GROQ_API_KEY: str
    GROQ_MODEL: str

    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5433
    POSTGRES_DB: str = "insight_ai"
    POSTGRES_USER: str = "insight_ai"
    POSTGRES_PASSWORD: str = ""


settings = Settings()
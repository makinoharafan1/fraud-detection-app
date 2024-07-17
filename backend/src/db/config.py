from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    POSTGRES_URL: str
    POSTGRES_DB: str
    POSTGRES_DB_USER: str
    POSTGRES_DB_PASSWORD: str
    POSTGRES_DB_HOST_PORT: str

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()

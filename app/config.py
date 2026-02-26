from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL_ASYNCPG_DRIVER: str
    VERSION: str

    # Lấy config từ file .env
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

Config = Settings()
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL_ASYNCPG_DRIVER: str
    VERSION: str
    SCRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    MINIO_URL: str
    MINIO_ACCESS_KEY: str
    MINIO_SECRET_KEY: str
    BUCKET_NAME: str
    LLM_MODEL= str
    OLLAMA_HOST= str
    PSYCOPG_CONNECT=str

    # Lấy config từ file .env
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

Config = Settings()
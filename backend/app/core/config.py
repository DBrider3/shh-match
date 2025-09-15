from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    # App settings
    APP_ENV: str = "dev"
    APP_SECRET: str
    API_BASE_PATH: str = "/"
    CORS_ORIGINS: str = "http://localhost:3000"
    LOG_LEVEL: str = "INFO"

    # Database
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "kakao_match"
    DB_USER: str = "app"
    DB_PASSWORD: str

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Security
    PASSWORD_HASH_SCHEME: str = "bcrypt"
    JWT_ISSUER: str = "kakao-match-api"
    JWT_AUDIENCE: str = "kakao-match-web"
    JWT_EXPIRE_MINUTES: int = 10080  # 7 days
    JWT_ALG: str = "HS256"

    # Timezone
    TZ: str = "Asia/Seoul"

    model_config = {"env_file": ".env"}

    @property
    def database_url(self) -> str:
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]


settings = Settings()
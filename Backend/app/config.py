from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    database_url: str = "sqlite+aiosqlite:///./rte.db"
    db_echo: bool = False
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = False
    allowed_origins: List[str] = ["http://localhost:5173", "http://localhost:3000"]
    api_secret_key: str = "secret"
    log_level: str = "INFO"
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)


settings = Settings()

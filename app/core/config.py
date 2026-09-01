from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "ISO20022 Auth Service"
    app_version: str = "1.0.0"
    frontend_url: str = "http://localhost:5173"
    backend_host: str = "localhost"
    backend_port: int = 8000
    secret_key: str = "CHANGE_SESSION_SECRET"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


settings = Settings()
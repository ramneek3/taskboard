from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "TaskBoard API"
    # Local default has no password. Compose, Kubernetes, and CI set DATABASE_URL
    # or POSTGRES_* explicitly. Do not put a real password here.
    database_url: str = "sqlite:///./taskboard.db"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()

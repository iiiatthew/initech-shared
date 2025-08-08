from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    secret_key: str = 'your-secret-key-here-please-change-in-production'
    database_url: str = 'sqlite:///./app.db'
    environment: str = 'development'
    project_name: str = 'FastAPI User & Role Testing Application'
    api_v1_str: str = '/api/v1'

    model_config = SettingsConfigDict(env_file='.env', case_sensitive=False)


settings = Settings()

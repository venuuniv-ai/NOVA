from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg://nova:nova_local_only@localhost:5432/nova"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()

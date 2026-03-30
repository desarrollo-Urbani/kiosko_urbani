from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = Field(
        default="postgresql+psycopg://postgres:postgres@localhost:5432/urbani_kiosco",
        alias="DATABASE_URL",
    )
    kiosk_token: str = Field(default="dev-kiosk-token", alias="KIOSK_TOKEN")
    average_attention_minutes: int = Field(default=15, alias="AVERAGE_ATTENTION_MINUTES")
    moby_base_url: str = Field(default="https://app-api.mobysuite.com", alias="MOBY_BASE_URL")
    moby_client_id: str = Field(default="", alias="MOBY_CLIENT_ID")
    moby_client_secret: str = Field(default="", alias="MOBY_CLIENT_SECRET")


settings = Settings()

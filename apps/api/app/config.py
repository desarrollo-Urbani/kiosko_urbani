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
    executive_allowed_emails: str = Field(default="", alias="EXECUTIVE_ALLOWED_EMAILS")
    supervisor_emails: str = Field(default="", alias="SUPERVISOR_EMAILS")
    admin_emails: str = Field(default="", alias="ADMIN_EMAILS")
    auth_session_ttl_minutes: int = Field(default=720, alias="AUTH_SESSION_TTL_MINUTES")


settings = Settings()

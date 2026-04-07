from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: Literal["development", "staging", "production"] = Field(default="development", alias="APP_ENV")
    debug: str = Field(default="true", alias="DEBUG")
    cors_allow_origins: str = Field(
        default="http://127.0.0.1:5173,http://localhost:5173,http://127.0.0.1:5174,http://localhost:5174,http://127.0.0.1:5175,http://localhost:5175",
        alias="CORS_ALLOW_ORIGINS",
    )

    database_url: str = Field(
        default="postgresql+psycopg://postgres:postgres@localhost:5432/urbani_kiosco",
        alias="DATABASE_URL",
    )
    db_pool_size: int = Field(default=2, alias="DB_POOL_SIZE")
    db_max_overflow: int = Field(default=0, alias="DB_MAX_OVERFLOW")
    db_pool_timeout: int = Field(default=30, alias="DB_POOL_TIMEOUT")
    kiosk_token: str = Field(default="dev-kiosk-token", alias="KIOSK_TOKEN")
    average_attention_minutes: int = Field(default=15, alias="AVERAGE_ATTENTION_MINUTES")
    moby_base_url: str = Field(default="https://app-api.mobysuite.com", alias="MOBY_BASE_URL")
    moby_client_id: str = Field(default="", alias="MOBY_CLIENT_ID")
    moby_client_secret: str = Field(default="", alias="MOBY_CLIENT_SECRET")
    executive_allowed_emails: str = Field(default="", alias="EXECUTIVE_ALLOWED_EMAILS")
    supervisor_emails: str = Field(default="desarrollo@urbani.cl", alias="SUPERVISOR_EMAILS")
    admin_emails: str = Field(default="", alias="ADMIN_EMAILS")
    auth_session_ttl_minutes: int = Field(default=720, alias="AUTH_SESSION_TTL_MINUTES")
    auth_mysql_enabled: bool = Field(default=False, alias="AUTH_MYSQL_ENABLED")
    auth_mysql_user: str = Field(default="", alias="AUTH_MYSQL_USER")
    auth_mysql_password: str = Field(default="", alias="AUTH_MYSQL_PASSWORD")
    auth_mysql_host: str = Field(default="", alias="AUTH_MYSQL_HOST")
    auth_mysql_port: int = Field(default=3306, alias="AUTH_MYSQL_PORT")
    auth_mysql_database: str = Field(default="", alias="AUTH_MYSQL_DATABASE")
    auth_mysql_users_view: str = Field(default="usuarios_view", alias="AUTH_MYSQL_USERS_VIEW")
    auth_mysql_email_column: str = Field(default="correo_electronico", alias="AUTH_MYSQL_EMAIL_COLUMN")
    auth_mysql_name_column: str = Field(default="nombre", alias="AUTH_MYSQL_NAME_COLUMN")
    auth_mysql_active_column: str = Field(default="activo", alias="AUTH_MYSQL_ACTIVE_COLUMN")

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"

    @property
    def is_staging(self) -> bool:
        return self.app_env == "staging"

    @property
    def is_development(self) -> bool:
        return self.app_env == "development"

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_allow_origins.split(",") if origin.strip()]

    @property
    def debug_enabled(self) -> bool:
        value = str(self.debug).strip().lower()
        if value in {"1", "true", "yes", "on", "debug"}:
            return True
        if value in {"0", "false", "no", "off", "release", "prod", "production"}:
            return False
        return False


settings = Settings()

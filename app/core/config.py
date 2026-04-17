from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False)

    app_name: str = "DojoFlow API"
    app_env: str = "development"
    secret_key: str = "change_this_secret"
    access_token_expire_minutes: int = 1440

    mysql_host: str = "localhost"
    mysql_port: int = 3306
    mysql_user: str = "root"
    mysql_password: str = "root"
    mysql_db: str = "dojoflow"
    database_url: str | None = None

    cors_origins: str = "http://localhost:5173"
    frontend_base_url: str = "http://localhost:5173"
    reset_password_expire_minutes: int = 30

    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str | None = None
    smtp_password: str | None = None
    smtp_from_email: str | None = None
    
    paypal_client_id: str | None = None
    paypal_client_secret: str | None = None
    paypal_base_url: str = "https://api-m.sandbox.paypal.com"
    paypal_success_url: str = "http://localhost:5173/app/payments"
    paypal_cancel_url: str = "http://localhost:5173/app/payments"
    paypal_plan_success_url: str = "http://localhost:5173/app/plans"
    paypal_plan_cancel_url: str = "http://localhost:5173/app/plans"

    mercado_pago_access_token: str | None = None

    @property
    def sqlalchemy_database_uri(self) -> str:
        if self.database_url:
            return self.database_url
        
        # Usa SQLite por defecto
        return "sqlite:///./dojoflow.db"


settings = Settings()
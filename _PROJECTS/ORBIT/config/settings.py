from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    # Server
    port: int = Field(8003, env="PORT")
    environment: str = Field("development", env="ENVIRONMENT")
    secret_key: str = Field(..., env="SECRET_KEY")
    allowed_hosts: str = Field("orbit.aurenix.cloud", env="ALLOWED_HOSTS")

    # Database
    database_url: str = Field(..., env="DATABASE_URL")

    # JWT
    jwt_secret_key: str = Field(..., env="JWT_SECRET_KEY")
    jwt_algorithm: str = Field("HS256", env="JWT_ALGORITHM")
    jwt_expire_hours: int = Field(8, env="JWT_EXPIRE_HOURS")

    # Rate limiting
    rate_limit_login: str = Field("10/5minutes", env="RATE_LIMIT_LOGIN")
    rate_limit_api: str = Field("200/minute", env="RATE_LIMIT_API")

    # Telegram
    telegram_bot_token: str = Field("", env="TELEGRAM_BOT_TOKEN")
    telegram_admin_chat_id: str = Field("", env="TELEGRAM_ADMIN_CHAT_ID")

    # Monitoring
    metrics_pull_interval_minutes: int = Field(60, env="METRICS_PULL_INTERVAL_MINUTES")
    metrics_pull_timeout_seconds: int = Field(10, env="METRICS_PULL_TIMEOUT_SECONDS")
    heartbeat_alert_after_minutes: int = Field(10, env="HEARTBEAT_ALERT_AFTER_MINUTES")

    # Alert thresholds
    alert_cpu_threshold_pct: float = Field(85.0, env="ALERT_CPU_THRESHOLD_PCT")
    alert_ram_threshold_pct: float = Field(90.0, env="ALERT_RAM_THRESHOLD_PCT")
    alert_disk_threshold_pct: float = Field(80.0, env="ALERT_DISK_THRESHOLD_PCT")
    alert_claude_cost_monthly_eur: float = Field(50.0, env="ALERT_CLAUDE_COST_MONTHLY_EUR")

    # n8n
    n8n_base_url: str = Field("http://localhost:5678", env="N8N_BASE_URL")
    n8n_api_key: str = Field("", env="N8N_API_KEY")

    # Internal API key (for n8n / machine-to-machine calls)
    internal_api_key: str = Field("", env="INTERNAL_API_KEY")

    # Hostinger VPS API (https://api.hostinger.com/v1/vps)
    hostinger_api_token: str = Field("", env="HOSTINGER_API_TOKEN")
    hostinger_vps_id: int = Field(1285851, env="HOSTINGER_VPS_ID")  # default: Aurenix VPS

    # Admin bootstrap
    admin_email: str = Field("admin@aurenix.es", env="ADMIN_EMAIL")
    admin_password: str = Field("", env="ADMIN_PASSWORD")

    @property
    def is_production(self) -> bool:
        return self.environment == "production"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


_settings: Settings | None = None


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings

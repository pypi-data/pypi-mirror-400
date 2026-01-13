from pydantic_settings import BaseSettings, SettingsConfigDict

# noinspection PyMethodMayBeStatic
class ServerSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore",
        env_file_encoding="utf-8"
    )

    # Backlog API Settings
    BACKLOG_API_KEY: str
    BACKLOG_DOMAIN: str  # e.g., "your-space.backlog.com"

settings = ServerSettings()

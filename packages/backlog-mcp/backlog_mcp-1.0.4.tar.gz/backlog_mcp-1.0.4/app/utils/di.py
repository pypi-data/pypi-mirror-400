from dataclasses import dataclass

@dataclass
class BacklogContext:
    api_key: str
    backlog_domain: str

def create_backlog_context() -> BacklogContext:
    """Create BacklogContext directly from environment variables."""
    from app.server_settings import settings
    return BacklogContext(
        api_key=settings.BACKLOG_API_KEY,
        backlog_domain=f"https://{settings.BACKLOG_DOMAIN}/"
    )

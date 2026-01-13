from app.utils.di import create_backlog_context
from app.utils.ultils import get_issue_detail_handler


async def get_issue_details(
    issue_key: str,
    include_comments: bool,
    timezone: str = "UTC",
):
    """
    Get details of a Backlog issue by its key.

    Args:
        issue_key (str): The key of the Backlog issue to retrieve.
        include_comments (bool): Whether to include comments in the response.
        timezone (str, optional): The timezone to format datetime fields. Defaults to "UTC".
    """
    try:
        if not issue_key:
            raise ValueError("Please provide an issue key.")
        ctx = create_backlog_context()
        result = await get_issue_detail_handler(
            backlog_domain=ctx.backlog_domain,
            api_key=ctx.api_key,
            issue_key=issue_key,
            timezone=timezone,
            include_comments=include_comments,
        )
        return result
    except Exception as e:
        raise e

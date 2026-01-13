from app.utils.di import create_backlog_context
from app.utils.ultils import get_user_task, get_current_user


async def get_user_issue_list():
    """
    Retrieves a list of issues assigned to the current user from Backlog.

    This function automatically determines the current user's ID via API
    and returns only issues assigned to that user.
    """

    try:
        ctx = create_backlog_context()

        # Fetch current user information
        current_user = await get_current_user(ctx.backlog_domain, ctx.api_key)
        current_user_id = current_user["id"]

        # Get issues assigned to current user
        issue_list = await get_user_task(
            backlog_domain=ctx.backlog_domain,
            api_key=ctx.api_key,
            assignee_ids=[current_user_id]
        )
        return issue_list
    except Exception as e:
        raise e

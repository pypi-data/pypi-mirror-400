import asyncio
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
import httpx
import pytz

from app.constants.constants import BacklogApiError
from app.logging_config import logger


def convert_to_timezone(timezone_str, utc_time_str):
    dt_utc = datetime.strptime(utc_time_str, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=ZoneInfo("UTC"))
    local_time = dt_utc.astimezone(ZoneInfo(timezone_str))

    return local_time.strftime(f"%Y-%m-%d %H:%M")


def time_range_from_yesterday_to_now(user_timezone: str):
    timezone = pytz.timezone(user_timezone)
    now = datetime.now(timezone)
    yesterday = now - timedelta(days=1)
    # update_until_date = yesterday.strftime('%Y-%m-%d')
    # update_since_date = update_until_date

    update_until_date = now.strftime('%Y-%m-%d')
    update_since_date = yesterday.strftime('%Y-%m-%d')
    is_monday = now.weekday() == 0
    if is_monday:
        friday = now - timedelta(days=3)
        update_since_date = friday.strftime('%Y-%m-%d')

    return update_since_date, update_until_date


def time_in_range(time: str, start_range: str, end_range: str):
    # Convert the input time to an offset-aware datetime
    time_to_be_compared = datetime.fromisoformat(time.replace("Z", "+00:00"))

    # Create offset-aware datetime for start and end range
    start_range_time = datetime.strptime(start_range, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    end_range_time = datetime.strptime(end_range, "%Y-%m-%d").replace(tzinfo=timezone.utc)

    # Set the end range time to the end of the day
    end_range_time = end_range_time.replace(hour=23, minute=59, second=59, microsecond=999999)

    return start_range_time <= time_to_be_compared <= end_range_time


def process_issue_detail(issue_detail, timezone, issue_key, include_comments: bool = True):
    processed_issue = {
        "issue_key": issue_key,
        "summary": issue_detail["summary"],
        "description": issue_detail["description"]
    }

    if include_comments:
        comments = issue_detail.get("comments", [])
        if comments:
            # Sort comments by created_at (created field)
            sorted_comments = sorted(comments, key=lambda c: convert_to_timezone(timezone, c["created"]))
            # Create list of {content, created_by} where created_by is just the name
            processed_comments = [
                {
                    "content": c["content"],
                    "created_by": c["createdUser"]["name"] if c.get("createdUser") else None
                }
                for c in sorted_comments if c.get("content")
            ]
            # Filter out None created_by if any (though should not happen)
            processed_comments = [c for c in processed_comments if c["created_by"]]
            processed_issue["comments"] = processed_comments

    return processed_issue


async def get_issue_detail_handler(
        backlog_domain: str,
        api_key: str,
        issue_key: str,
        timezone: str,
        include_comments: bool = True,
):
    issue_comments_url = f"{backlog_domain}api/v2/issues/{issue_key}/comments"
    issue_detail_url = f"{backlog_domain}api/v2/issues/{issue_key}"
    params = {"apiKey": api_key}

    async with httpx.AsyncClient() as client:
        try:
            issue_detail_response = client.get(issue_detail_url, params=params)
            
            if include_comments:
                comments_response = client.get(issue_comments_url, params=params)
                results = await asyncio.gather(issue_detail_response, comments_response)
                issue_detail_result = results[0]
                comments_result = results[1]
                issue_detail = issue_detail_result.json()
                issue_comment = comments_result.json()
            else:
                issue_detail_result = await issue_detail_response
                issue_detail = issue_detail_result.json()
                issue_comment = []

            if not issue_detail_result.is_success:
                error_code = issue_detail["errors"][0]["code"]
                return {
                    "error_msg": BacklogApiError.get_description_by_code(error_code),
                }

            if include_comments and not comments_result.is_success:
                error_code = issue_comment["errors"][0]["code"]
                return {
                    "error_msg": BacklogApiError.get_description_by_code(error_code),
                }

            if include_comments:
                comments_in_time_range = []
                for comment in issue_comment:
                    comments_in_time_range.append(comment)
                issue_detail.update({"comments": comments_in_time_range})

            processed_detail = process_issue_detail(issue_detail, timezone, issue_key, include_comments)
            return processed_detail

        except Exception as e:
            logger.exception("Error while processing issue_detail")
            raise e

async def get_project_status_id_list(backlog_domain: str, api_key: str, project_id: int):
    url = f"{backlog_domain}api/v2/projects/{project_id}/statuses"
    params = {"apiKey": api_key}
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, timeout=10.0, params=params)
            response.raise_for_status()
            data = response.json()
            if isinstance(data, list):
                status_ids = [item["id"] for item in data if item["id"] != 4]
                return status_ids
            else:
                raise ValueError("Unexpected response format: expected a list of statuses")
        except httpx.HTTPError as e:
            raise ValueError(f"Failed to get status list for project {project_id}: {e}") from e
        except Exception as e:
            raise ValueError(f"Unexpected error while getting status list for project {project_id}: {e}") from e


async def get_user_task(
    backlog_domain: str,
    api_key: str,
    project_ids: list[int] | None = None,
    assignee_ids: list[int] | None = None,
    status_ids: list[int] | None = None,
    milestone_ids: list[int] | None = None,
    parent_issue_ids: list[int] | None = None,
    created_since: str | None = None,
    created_until: str | None = None,
    updated_since: str | None = None,
    updated_until: str | None = None,
    start_date_since: str | None = None,
    start_date_until: str | None = None,
    due_date_since: str | None = None,
    due_date_until: str | None = None,
):
    try:
        url = f"{backlog_domain}api/v2/issues"
        params = {
            "count": 100,
            "sort": "updated",
            "apiKey": api_key
        }

        if assignee_ids:
            for aid in assignee_ids:
                params.setdefault("assigneeId[]", []).append(aid)

        # Handle project IDs (fetch all if not provided)
        if not project_ids:
            project_ids = await get_project_list(backlog_domain, api_key)

        for pid in project_ids:
            params.setdefault("projectId[]", []).append(pid)

        if not status_ids:
            async def fetch_status(p_id):
                return await get_project_status_id_list(backlog_domain, api_key, p_id)

            tasks = [fetch_status(p_id) for p_id in project_ids]

            results = await asyncio.gather(*tasks)

            collected_status_ids = set()
            for status_list in results:
                if status_list:
                    collected_status_ids.update(status_list)

            status_ids = list(collected_status_ids) if collected_status_ids else [1, 2, 3]

        for sid in status_ids:
            params.setdefault("statusId[]", []).append(sid)


        # Check for milestone IDs without project IDs
        if milestone_ids and not project_ids:
            raise ValueError("Please provide the project name to continue.")

        # Add milestone ID filters
        if milestone_ids:
            for mid in milestone_ids:
                params.setdefault("milestoneId[]", []).append(mid)

        # Add parent issue ID filters
        if parent_issue_ids:
            for pid in parent_issue_ids:
                params.setdefault("parentIssueId[]", []).append(pid)

        # Add optional date filters
        if created_since:
            params["createdSince"] = created_since
        if created_until:
            params["createdUntil"] = created_until

        if updated_since:
            params["updatedSince"] = updated_since
        if updated_until:
            params["updatedUntil"] = updated_until

        if start_date_since:
            params["startDateSince"] = start_date_since
        if start_date_until:
            params["startDateUntil"] = start_date_until

        if due_date_since:
            params["dueDateSince"] = due_date_since
        if due_date_until:
            params["dueDateUntil"] = due_date_until

        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, timeout=10.0)
            response.raise_for_status()
            data = response.json()

            issue_list = [
                {
                    "issueKey": issue["issueKey"],
                    "title": issue["summary"]
                }
                for issue in data
            ]

            print(f"Total issues: {len(issue_list)}")
            return issue_list
    except httpx.HTTPStatusError as e:
        try:
            body = e.response.json()
            error_code = None
            if "errors" in body and body["errors"]:
                error_code = body["errors"][0].get("code")
            raise ValueError(f"API error: {BacklogApiError.get_description_by_code(error_code)}") from e
        except Exception:
            raise ValueError("Failed to parse error response") from e
    except Exception as e:
        raise ValueError(f"Request failed: {str(e)}") from e


async def get_project_list(backlog_domain: str, api_key: str) -> list[int]:
    url = f"{backlog_domain}api/v2/projects"
    params = {"apiKey": api_key}

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, params=params, timeout=10.0)
            response.raise_for_status()
            data = response.json()
            return [project["id"] for project in data if "id" in project]
        except httpx.HTTPError as e:
            raise ValueError(f"Failed to get project list: {e}") from e
        except Exception as e:
            raise ValueError(f"Unexpected error while getting project list: {e}") from e


async def get_current_user(backlog_domain: str, api_key: str) -> dict:
    """Get current user information from Backlog API.

    Returns:
        dict: {"id": int, "name": str}
    """
    url = f"{backlog_domain}api/v2/users/myself"
    params = {"apiKey": api_key}

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, params=params, timeout=10.0)
            response.raise_for_status()
            data = response.json()
            return {
                "id": data["id"],
                "name": data["name"]
            }
        except httpx.HTTPError as e:
            raise ValueError(f"Failed to get current user: {e}") from e
        except Exception as e:
            raise ValueError(f"Unexpected error while getting current user: {e}") from e

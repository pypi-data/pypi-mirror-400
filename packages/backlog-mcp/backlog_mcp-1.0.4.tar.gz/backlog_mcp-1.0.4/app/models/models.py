from enum import Enum

from pydantic import BaseModel, Field
from typing import Optional, List, Annotated


class Project(BaseModel):
    leader_id: Optional[int] = None
    backlog_project_key: str
    name: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    description: Optional[str] = None
    backlog_project_id: int
    issue_template_version_id: Optional[int] = None
    status_template_version_id: Optional[int] = None


class ProjectImportRequest(BaseModel):
    data: List[Project]


class ProjectEventRequest(BaseModel):
    payload: Project


class BacklogTemplate(BaseModel):
    template_version_id: Optional[int] = None
    name: Optional[str] = None
    description: Optional[str] = None
    summary: Optional[str] = None
    template_type: Optional[str] = None


class BacklogTemplateImportRequest(BaseModel):
    data: List[BacklogTemplate]


class MemberRole(BaseModel):
    email: Optional[str] = None
    team: Optional[str] = None
    role: Optional[str] = None


class MemberRolesImportRequest(BaseModel):
    data: List[MemberRole]


class IssueType(str, Enum):
    JP_FEEDBACK = "JP Feedback"
    JP_REQUEST = "JP Request"
    BUG = "Bug"
    JP_BUG = "JP Bug"
    RELEASE = "Release"
    TASK = "Task"
    OTHERS = "Others"
    QC_REPORT = "QC Report"
    USER_STORY = "User Story"
    QC_TASK = "QC Task"
    REMAIN = "Remain"
    FE_TASK = "FE Task"
    BE_TASK = "BE Task"


class Priority(str, Enum):
    HIGH = "High"
    NORMAL = "Normal"
    LOW = "Low"


class PriorityID(Enum):
    HIGH = 2
    NORMAL = 3
    LOW = 4

    @classmethod
    def get_id(cls, name: str) -> int:
        name = name.upper()
        if name in cls.__members__:
            return cls[name].value
        raise ValueError(f"Invalid priority name: {name}")


class Task(BaseModel):
    summary: Annotated[str, Field(description="Title of the task")]
    description: Annotated[str, Field(description="Description of a task following a predefined template for each issue type")]
    project_id: Annotated[int, Field(description="ID of the project")]
    project_name: Annotated[str, Field(description="Name of the project")]
    issue_type: Annotated[IssueType, Field(description="Type of the issue")]
    parent_issue_key: Annotated[str | None, Field(description="Issue key of the parent issue")] = None
    priority: Annotated[Priority | None, Field(description="Priority of the issue")] = Priority.NORMAL
    assignee_id: Annotated[int | None, Field(description="ID of the user, example: 12345")] = None
    assignee_email: Annotated[str | None, Field(description="email of the assignee")] = None
    start_date: Annotated[str | None, Field(description="Task start date (yyyy-MM-dd)")] = None
    due_date: Annotated[str | None, Field(description="Task deadline (yyyy-MM-dd)")] = None
    estimated_hours: Annotated[float | None, Field(description="Estimated time in hours")] = None
    milestone_id: Annotated[int | None, Field(description="ID of the milestone")] = None
    milestone_name: Annotated[str | None, Field(description="Name of the milestone")] = None


class Status(str, Enum):
    OPEN = "Open"
    IN_PROGRESS = "In Progress"
    RESOLVED = "Resolved"
    CLOSED = "Closed"

    @property
    def id(self) -> int:
        return {
            Status.OPEN: 1,
            Status.IN_PROGRESS: 2,
            Status.RESOLVED: 3,
            Status.CLOSED: 4
        }[self]


class IssueUpdate(BaseModel):
    issue_key: Annotated[str, Field(description="issue key")]
    new_status: Annotated[Status, Field(description="target new status of the issue")]


class DescriptionTemplate(BaseModel):
    project_id: Annotated[int, Field(description="ID of the project")]
    project_name: Annotated[str, Field(description="Name of the project")]
    issue_type: Annotated[IssueType, Field(description="Type of the issue")]


class CreateTaskModel(BaseModel):
    tasks: List[Task]


class Assignee(BaseModel):
    name: Optional[str] = ""
    email: Optional[str] = None
    assignee_id: Optional[int] = None
    embedded_text: Optional[str] = "    "


class AssigneesImportRequest(BaseModel):
    data: List[Assignee]

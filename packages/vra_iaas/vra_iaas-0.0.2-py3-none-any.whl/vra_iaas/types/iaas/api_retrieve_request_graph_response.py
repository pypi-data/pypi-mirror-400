# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from pydantic import Field as FieldInfo

from ..._models import BaseModel
from .api.project import Project

__all__ = ["APIRetrieveRequestGraphResponse", "Task", "TaskStage", "TaskStageTaskInfo", "TaskStageTransitionSource"]


class TaskStageTaskInfo(BaseModel):
    """Transition Source Of Provisioning Request"""

    duration_micros: Optional[int] = FieldInfo(alias="durationMicros", default=None)

    failure_message: Optional[str] = FieldInfo(alias="failureMessage", default=None)

    stage: Optional[str] = None
    """ID of Provisioning Request Stage in the task"""


class TaskStageTransitionSource(BaseModel):
    """Transition Source Of Provisioning Request"""

    id: Optional[str] = None
    """ID of Provisioning Request Stage in the task"""

    sub_stage: Optional[str] = FieldInfo(alias="subStage", default=None)
    """Source SubStage Of Provisioning Request in the task"""

    timestamp_micros: Optional[int] = FieldInfo(alias="timestampMicros", default=None)
    """Time In Micros of stage transition from source stage."""


class TaskStage(BaseModel):
    """Provisioning Request Stage"""

    resource_links: Optional[List[str]] = FieldInfo(alias="resourceLinks", default=None)
    """Collection of resources"""

    task_info: Optional[TaskStageTaskInfo] = FieldInfo(alias="taskInfo", default=None)
    """Transition Source Of Provisioning Request"""

    task_sub_stage: Optional[str] = FieldInfo(alias="taskSubStage", default=None)
    """SubStage Of Provisioning Request Task"""

    timestamp_micros: Optional[int] = FieldInfo(alias="timestampMicros", default=None)

    transition_source: Optional[TaskStageTransitionSource] = FieldInfo(alias="transitionSource", default=None)
    """Transition Source Of Provisioning Request"""


class Task(BaseModel):
    """Task Service Document History"""

    id: Optional[str] = None
    """ID Of Provisioning Request Task."""

    stages: Optional[List[TaskStage]] = None
    """Collection of Task Service Stages with transition details."""


class APIRetrieveRequestGraphResponse(BaseModel):
    """Result Of Request Graph For Provisioning Request"""

    project: Optional[Project] = None
    """
    Projects link users and cloud zones, thus controlling who can use what cloud
    resources. **HATEOAS** links: **self** - Project - Self link to this project
    """

    tasks: Optional[List[Task]] = None
    """Collection of Task Service Document History"""

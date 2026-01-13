# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from datetime import datetime

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["TaskCreateResponse"]


class TaskCreateResponse(BaseModel):
    id: str

    created_at: datetime = FieldInfo(alias="createdAt")

    description: str

    html_url: str = FieldInfo(alias="htmlUrl")
    """URL to view this task in the Tembo web application"""

    organization_id: str = FieldInfo(alias="organizationId")

    status: str

    title: str

    updated_at: datetime = FieldInfo(alias="updatedAt")

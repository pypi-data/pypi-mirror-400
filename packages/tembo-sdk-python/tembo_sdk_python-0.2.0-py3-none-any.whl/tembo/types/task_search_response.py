# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List
from datetime import datetime

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["TaskSearchResponse", "Issue", "Meta"]


class Issue(BaseModel):
    id: str

    created_at: datetime = FieldInfo(alias="createdAt")

    description: str

    html_url: str = FieldInfo(alias="htmlUrl")
    """URL to view this task in the Tembo web application"""

    organization_id: str = FieldInfo(alias="organizationId")

    status: str

    title: str

    updated_at: datetime = FieldInfo(alias="updatedAt")


class Meta(BaseModel):
    current_page: int = FieldInfo(alias="currentPage")

    has_next: bool = FieldInfo(alias="hasNext")

    has_previous: bool = FieldInfo(alias="hasPrevious")

    page_size: int = FieldInfo(alias="pageSize")

    total_count: int = FieldInfo(alias="totalCount")

    total_pages: int = FieldInfo(alias="totalPages")


class TaskSearchResponse(BaseModel):
    issues: List[Issue]

    meta: Meta

    query: str

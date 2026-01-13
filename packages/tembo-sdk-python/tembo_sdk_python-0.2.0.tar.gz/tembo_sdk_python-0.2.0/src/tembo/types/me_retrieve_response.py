# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["MeRetrieveResponse"]


class MeRetrieveResponse(BaseModel):
    org_id: Optional[str] = FieldInfo(alias="orgId", default=None)
    """Organization ID for the authenticated user"""

    user_id: Optional[str] = FieldInfo(alias="userId", default=None)
    """User ID for the authenticated user"""

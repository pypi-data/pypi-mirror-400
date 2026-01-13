# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Optional
from datetime import datetime

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["RepositoryListResponse", "CodeRepository", "CodeRepositoryIntegration"]


class CodeRepositoryIntegration(BaseModel):
    """Associated integration details"""

    id: str
    """Unique identifier for the integration"""

    configuration: Dict[str, object]
    """Integration configuration settings"""

    name: str
    """Name of the integration"""

    type: str
    """Type of integration (e.g., github, gitlab)"""


class CodeRepository(BaseModel):
    id: str
    """Unique identifier for the code repository"""

    created_at: datetime = FieldInfo(alias="createdAt")
    """Timestamp when the repository record was created"""

    enabled_at: datetime = FieldInfo(alias="enabledAt")
    """Timestamp when the repository was enabled"""

    name: str
    """Name of the repository"""

    organization_id: str = FieldInfo(alias="organizationId")
    """Organization ID that owns this repository"""

    updated_at: datetime = FieldInfo(alias="updatedAt")
    """Timestamp when the repository record was last updated"""

    branch: Optional[str] = None
    """Default branch name"""

    description: Optional[str] = None
    """Repository description"""

    integration: Optional[CodeRepositoryIntegration] = None
    """Associated integration details"""

    url: Optional[str] = None
    """Repository URL"""


class RepositoryListResponse(BaseModel):
    code_repositories: List[CodeRepository] = FieldInfo(alias="codeRepositories")
    """Array of enabled code repositories for the organization"""

# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["TaskSearchParams"]


class TaskSearchParams(TypedDict, total=False):
    q: Required[str]
    """Search query to find issues by title or description"""

    limit: int
    """Number of items to return per page (max 100)"""

    page: int
    """Page number to retrieve (starts from 1)"""

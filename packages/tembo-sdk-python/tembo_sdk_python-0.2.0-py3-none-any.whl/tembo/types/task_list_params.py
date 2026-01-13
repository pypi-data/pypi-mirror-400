# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

__all__ = ["TaskListParams"]


class TaskListParams(TypedDict, total=False):
    limit: int
    """Number of items to return per page (max 100)"""

    page: int
    """Page number to retrieve (starts from 1)"""

# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List
from typing_extensions import Literal

from .project import Project
from .._models import BaseModel

__all__ = ["ProjectListResponse"]


class ProjectListResponse(BaseModel):
    """Response containing the list of projects for a team"""

    data: List[Project]
    """Data contains the project items"""

    status: Literal["success"]
    """Status indicates the response status "success" """

# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List
from typing_extensions import Literal

from .storage import Storage
from .._models import BaseModel

__all__ = ["StorageListResponse"]


class StorageListResponse(BaseModel):
    """Response containing the list of storages configurations for a project"""

    data: List[Storage]
    """Data contains the storage items"""

    status: Literal["success"]
    """Status indicates the response status "success" """

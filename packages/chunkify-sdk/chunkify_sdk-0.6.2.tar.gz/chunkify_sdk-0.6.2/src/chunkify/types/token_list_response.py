# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List
from typing_extensions import Literal

from .token import Token
from .._models import BaseModel

__all__ = ["TokenListResponse"]


class TokenListResponse(BaseModel):
    """Response containing the list of all tokens for a team.

    Including project and team tokens.
    """

    data: List[Token]
    """Data contains the token items"""

    status: Literal["success"]
    """Status indicates the response status "success" """

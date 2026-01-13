# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List
from typing_extensions import Literal

from .webhook import Webhook
from .._models import BaseModel

__all__ = ["WebhookListResponse"]


class WebhookListResponse(BaseModel):
    """Response containing the list of all webhooks for a project"""

    data: List[Webhook]
    """Data contains the webhook items"""

    status: Literal["success"]
    """Status indicates the response status "success" """

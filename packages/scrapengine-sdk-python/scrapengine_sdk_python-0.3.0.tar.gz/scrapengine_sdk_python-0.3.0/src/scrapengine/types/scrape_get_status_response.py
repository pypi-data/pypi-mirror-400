# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime
from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["ScrapeGetStatusResponse"]


class ScrapeGetStatusResponse(BaseModel):
    data: Optional[object] = None
    """The scraped data if completed"""

    metrics: Optional[str] = None

    status: Optional[Literal["pending", "processing", "success", "failed"]] = None
    """Job status"""

    timestamp: Optional[datetime] = None

# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["ScrapeCreateResponse", "Metadata"]


class Metadata(BaseModel):
    model: Optional[str] = None
    """Model used for extraction"""

    tokens_used: Optional[int] = FieldInfo(alias="tokensUsed", default=None)
    """Number of tokens used for extraction"""


class ScrapeCreateResponse(BaseModel):
    data: Optional[object] = None
    """The scraped data (format depends on request options)"""

    metadata: Optional[Metadata] = None

    metrics: Optional[str] = None
    """Performance metrics"""

    status: Optional[str] = None
    """Status of the scraping operation"""

    timestamp: Optional[datetime] = None
    """Timestamp of the response"""

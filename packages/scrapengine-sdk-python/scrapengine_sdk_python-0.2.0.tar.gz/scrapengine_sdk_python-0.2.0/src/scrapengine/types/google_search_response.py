# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["GoogleSearchResponse", "Ad", "OrganicResult", "Pagination", "SearchInformation"]


class Ad(BaseModel):
    description: Optional[str] = None

    display_link: Optional[str] = FieldInfo(alias="displayLink", default=None)

    link: Optional[str] = None

    position: Optional[int] = None

    title: Optional[str] = None


class OrganicResult(BaseModel):
    date: Optional[str] = None
    """Published date if available"""

    display_link: Optional[str] = FieldInfo(alias="displayLink", default=None)
    """Display URL"""

    link: Optional[str] = None
    """Result URL"""

    position: Optional[int] = None
    """Result position"""

    snippet: Optional[str] = None
    """Result snippet/description"""

    title: Optional[str] = None
    """Result title"""


class Pagination(BaseModel):
    current: Optional[int] = None

    next: Optional[str] = None


class SearchInformation(BaseModel):
    search_time: Optional[float] = FieldInfo(alias="searchTime", default=None)
    """Search time in seconds"""

    total_results: Optional[str] = FieldInfo(alias="totalResults", default=None)
    """Total number of results"""


class GoogleSearchResponse(BaseModel):
    ads: Optional[List[Ad]] = None

    organic_results: Optional[List[OrganicResult]] = FieldInfo(alias="organicResults", default=None)

    pagination: Optional[Pagination] = None

    related_searches: Optional[List[str]] = FieldInfo(alias="relatedSearches", default=None)

    search_information: Optional[SearchInformation] = FieldInfo(alias="searchInformation", default=None)

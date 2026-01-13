# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["BingSearchResponse", "OrganicResult", "Pagination", "SearchInformation"]


class OrganicResult(BaseModel):
    date: Optional[str] = None

    display_link: Optional[str] = FieldInfo(alias="displayLink", default=None)

    link: Optional[str] = None

    position: Optional[int] = None

    snippet: Optional[str] = None

    title: Optional[str] = None


class Pagination(BaseModel):
    current: Optional[int] = None

    next: Optional[str] = None


class SearchInformation(BaseModel):
    search_time: Optional[float] = FieldInfo(alias="searchTime", default=None)

    total_results: Optional[str] = FieldInfo(alias="totalResults", default=None)


class BingSearchResponse(BaseModel):
    organic_results: Optional[List[OrganicResult]] = FieldInfo(alias="organicResults", default=None)

    pagination: Optional[Pagination] = None

    related_searches: Optional[List[str]] = FieldInfo(alias="relatedSearches", default=None)

    search_information: Optional[SearchInformation] = FieldInfo(alias="searchInformation", default=None)

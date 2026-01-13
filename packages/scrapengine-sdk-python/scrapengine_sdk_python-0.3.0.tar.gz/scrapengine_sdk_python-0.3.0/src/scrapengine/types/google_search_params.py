# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["GoogleSearchParams"]


class GoogleSearchParams(TypedDict, total=False):
    q: Required[str]
    """Search query"""

    async_: Annotated[bool, PropertyInfo(alias="async")]
    """Run asynchronously and return job ID"""

    device: Literal["desktop", "mobile", "tablet"]
    """Device type for user agent simulation"""

    filter: Literal[0, 1]
    """Filter duplicate results (0=show all, 1=filter)"""

    gl: str
    """Country code (ISO 3166-1 alpha-2)"""

    google_domain: Annotated[str, PropertyInfo(alias="googleDomain")]
    """Google domain to use"""

    hl: str
    """Language code (ISO 639-1)"""

    location: str
    """Location for geo-targeted results"""

    nfpr: Literal[0, 1]
    """Disable auto-correct (0=allow, 1=disable)"""

    num: int
    """Number of results to return (1-100)"""

    raw_html: Annotated[bool, PropertyInfo(alias="rawHtml")]
    """Return raw HTML instead of parsed results"""

    safe: Literal["off", "medium", "high"]
    """Safe search mode"""

    start: int
    """Pagination offset"""

    tbm: Literal["search", "images", "news", "videos"]
    """Search type"""

    tbs: str
    """Time-based filter (qdr:d=day, qdr:w=week, qdr:m=month, qdr:y=year)"""

    uule: str
    """Encoded location for geo-targeted results (UULE format)"""

# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["BingSearchParams"]


class BingSearchParams(TypedDict, total=False):
    q: Required[str]
    """Search query"""

    async_: Annotated[bool, PropertyInfo(alias="async")]
    """Run asynchronously and return job ID"""

    cc: str
    """Country code"""

    count: int
    """Number of results (1-50)"""

    device: Literal["desktop", "mobile", "tablet"]
    """Device type"""

    freshness: Literal["Day", "Week", "Month"]
    """Freshness filter"""

    location: str
    """Location for geo-targeted results"""

    mkt: str
    """Market code (language-country format)"""

    offset: int
    """Pagination offset"""

    raw_html: Annotated[bool, PropertyInfo(alias="rawHtml")]
    """Return raw HTML instead of parsed results"""

    response_filter: Annotated[Literal["Webpages", "Images", "Videos", "News"], PropertyInfo(alias="responseFilter")]
    """Response content filter"""

    safe_search: Annotated[Literal["Off", "Moderate", "Strict"], PropertyInfo(alias="safeSearch")]
    """Safe search mode"""

    set_lang: Annotated[str, PropertyInfo(alias="setLang")]
    """UI language"""

    text_decorations: Annotated[bool, PropertyInfo(alias="textDecorations")]
    """Add bold markers around search terms"""

    text_format: Annotated[Literal["Raw", "HTML"], PropertyInfo(alias="textFormat")]
    """Text format"""

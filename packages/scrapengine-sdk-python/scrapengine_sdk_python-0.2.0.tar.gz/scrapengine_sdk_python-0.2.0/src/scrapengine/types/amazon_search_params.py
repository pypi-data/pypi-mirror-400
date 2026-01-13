# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["AmazonSearchParams"]


class AmazonSearchParams(TypedDict, total=False):
    q: Required[str]
    """Search query"""

    amazon_domain: Annotated[
        Literal[
            "www.amazon.com",
            "www.amazon.co.uk",
            "www.amazon.de",
            "www.amazon.fr",
            "www.amazon.co.jp",
            "www.amazon.in",
            "www.amazon.ca",
            "www.amazon.es",
            "www.amazon.it",
            "www.amazon.com.au",
        ],
        PropertyInfo(alias="amazonDomain"),
    ]
    """Amazon domain to use"""

    async_: Annotated[bool, PropertyInfo(alias="async")]
    """Run asynchronously and return job ID"""

    country: str
    """Country code for localized results"""

    department: str
    """Department/Category filter"""

    page: int
    """Page number"""

    price_max: Annotated[float, PropertyInfo(alias="priceMax")]
    """Maximum price filter"""

    price_min: Annotated[float, PropertyInfo(alias="priceMin")]
    """Minimum price filter"""

    prime: bool
    """Filter by Prime eligible products"""

    raw_html: Annotated[bool, PropertyInfo(alias="rawHtml")]
    """Return raw HTML instead of parsed results"""

    sort_by: Annotated[
        Literal["relevanceblender", "price-asc-rank", "price-desc-rank", "review-rank", "date-desc-rank"],
        PropertyInfo(alias="sortBy"),
    ]
    """Sort order"""

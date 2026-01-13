# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["LazadaSearchParams"]


class LazadaSearchParams(TypedDict, total=False):
    q: Required[str]
    """Search query"""

    async_: Annotated[bool, PropertyInfo(alias="async")]
    """Run asynchronously and return job ID"""

    category: str
    """Category filter"""

    country: str
    """Country code for localized results"""

    lazada_domain: Annotated[
        Literal[
            "www.lazada.sg",
            "www.lazada.com.my",
            "www.lazada.co.th",
            "www.lazada.com.ph",
            "www.lazada.co.id",
            "www.lazada.vn",
        ],
        PropertyInfo(alias="lazadaDomain"),
    ]
    """Lazada domain to use"""

    laz_mall: Annotated[bool, PropertyInfo(alias="lazMall")]
    """Filter by LazMall products only"""

    location: str
    """Location filter"""

    page: int
    """Page number"""

    price_max: Annotated[float, PropertyInfo(alias="priceMax")]
    """Maximum price filter"""

    price_min: Annotated[float, PropertyInfo(alias="priceMin")]
    """Minimum price filter"""

    rating: float
    """Minimum rating filter (0-5)"""

    raw_json: Annotated[bool, PropertyInfo(alias="rawJson")]
    """Return raw JSON response"""

    sort_by: Annotated[Literal["relevance", "priceasc", "pricedesc", "sales", "rating"], PropertyInfo(alias="sortBy")]
    """Sort order"""

# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = [
    "LazadaSearchResponse",
    "Pagination",
    "Product",
    "ProductPrice",
    "ProductRating",
    "ProductSeller",
    "SearchInfo",
]


class Pagination(BaseModel):
    current_page: Optional[int] = FieldInfo(alias="currentPage", default=None)

    next_page: Optional[str] = FieldInfo(alias="nextPage", default=None)

    total_pages: Optional[int] = FieldInfo(alias="totalPages", default=None)


class ProductPrice(BaseModel):
    currency: Optional[str] = None
    """Currency code"""

    current: Optional[float] = None
    """Current price"""

    discount_percent: Optional[float] = FieldInfo(alias="discountPercent", default=None)
    """Discount percentage"""

    original: Optional[float] = None
    """Original price before discount"""


class ProductRating(BaseModel):
    count: Optional[int] = None
    """Number of ratings"""

    value: Optional[float] = None
    """Rating value (0-5)"""


class ProductSeller(BaseModel):
    is_laz_mall: Optional[bool] = FieldInfo(alias="isLazMall", default=None)

    name: Optional[str] = None

    rating: Optional[float] = None


class Product(BaseModel):
    free_shipping: Optional[bool] = FieldInfo(alias="freeShipping", default=None)

    image: Optional[str] = None

    item_id: Optional[str] = FieldInfo(alias="itemId", default=None)
    """Lazada item ID"""

    link: Optional[str] = None

    location: Optional[str] = None

    position: Optional[int] = None

    price: Optional[ProductPrice] = None

    rating: Optional[ProductRating] = None

    seller: Optional[ProductSeller] = None

    sold: Optional[int] = None
    """Number of units sold"""

    title: Optional[str] = None


class SearchInfo(BaseModel):
    market: Optional[str] = None

    page: Optional[int] = None

    query: Optional[str] = None

    total_results: Optional[int] = FieldInfo(alias="totalResults", default=None)


class LazadaSearchResponse(BaseModel):
    pagination: Optional[Pagination] = None

    products: Optional[List[Product]] = None

    search_info: Optional[SearchInfo] = FieldInfo(alias="searchInfo", default=None)

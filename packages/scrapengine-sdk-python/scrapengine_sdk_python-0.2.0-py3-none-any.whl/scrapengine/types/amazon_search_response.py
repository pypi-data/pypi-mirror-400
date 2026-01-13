# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["AmazonSearchResponse", "Pagination", "Product", "ProductPrice", "ProductRating", "SearchInfo"]


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


class Product(BaseModel):
    asin: Optional[str] = None
    """Amazon Standard Identification Number"""

    badge: Optional[str] = None
    """Product badge (e.g., 'Best Seller')"""

    image: Optional[str] = None
    """Product image URL"""

    is_prime: Optional[bool] = FieldInfo(alias="isPrime", default=None)
    """Prime eligible"""

    is_sponsored: Optional[bool] = FieldInfo(alias="isSponsored", default=None)
    """Sponsored product"""

    link: Optional[str] = None
    """Product URL"""

    position: Optional[int] = None
    """Product position in results"""

    price: Optional[ProductPrice] = None

    rating: Optional[ProductRating] = None

    title: Optional[str] = None
    """Product title"""


class SearchInfo(BaseModel):
    page: Optional[int] = None

    query: Optional[str] = None

    total_results: Optional[int] = FieldInfo(alias="totalResults", default=None)


class AmazonSearchResponse(BaseModel):
    pagination: Optional[Pagination] = None

    products: Optional[List[Product]] = None

    search_info: Optional[SearchInfo] = FieldInfo(alias="searchInfo", default=None)

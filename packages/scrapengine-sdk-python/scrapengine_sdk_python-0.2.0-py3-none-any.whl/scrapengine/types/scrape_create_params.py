# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict
from typing_extensions import Literal, Required, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["ScrapeCreateParams", "Extract"]


class ScrapeCreateParams(TypedDict, total=False):
    url: Required[str]
    """The URL to scrape"""

    async_: Annotated[bool, PropertyInfo(alias="async")]
    """Run asynchronously and return job ID"""

    body: Dict[str, object]
    """Request body for POST/PUT/PATCH requests"""

    country: str
    """Proxy country for geo-targeted requests"""

    extract: Extract
    """AI-powered data extraction options"""

    format: Literal["raw", "json", "markdown"]
    """Response format"""

    headers: Dict[str, str]
    """Custom HTTP headers for the request"""

    include_headers: Annotated[bool, PropertyInfo(alias="includeHeaders")]
    """Include response headers in the result"""

    method: Literal["get", "post", "put", "delete", "patch", "head", "options"]
    """HTTP method for the request"""

    render: bool
    """Render JavaScript on the page using a headless browser"""


class Extract(TypedDict, total=False):
    """AI-powered data extraction options"""

    include_metadata: Annotated[bool, PropertyInfo(alias="includeMetadata")]
    """Include extraction metadata in response"""

    model: Literal["gpt-4o", "gpt-4o-mini", "claude-3-5-sonnet"]
    """LLM model to use for extraction"""

    prompt: str
    """Natural language prompt describing what to extract"""

    schema: Dict[str, object]
    """JSON Schema defining the structure to extract"""

    system_prompt: Annotated[str, PropertyInfo(alias="systemPrompt")]
    """Custom system prompt to guide the LLM behavior"""

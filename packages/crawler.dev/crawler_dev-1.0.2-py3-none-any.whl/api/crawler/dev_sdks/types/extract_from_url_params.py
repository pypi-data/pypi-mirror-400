# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, List, Union
from typing_extensions import Literal, Required, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["ExtractFromURLParams", "Proxy"]


class ExtractFromURLParams(TypedDict, total=False):
    url: Required[str]
    """The URL to extract text from."""

    cache_age: Annotated[Union[int, str], PropertyInfo(alias="cacheAge")]
    """Maximum acceptable age of cached content.

    This parameter controls how fresh cached data must be to be used.

    - If a cached item exists and is younger than this value, it will be used (cache
      hit)
    - If a cached item exists but is older than this value, it will be ignored and
      fresh data will be fetched (cache miss)
    - If set to 0, caching is disabled for this request (always fetches fresh data)
    - When fresh data is fetched, it will be cached with this value as the TTL for
      future requests Accepts either:
    - Integer: milliseconds (e.g., 86400000 for 1 day)
    - String: time format with unit (e.g., "1s", "5h", "3m", "4.4h", "2d") Supported
      units: s (seconds), m (minutes), h (hours), d (days), ms (milliseconds) Must
      be between 0 (no caching) and 3 days. Defaults to "2d" (2 days) if not
      specified. Examples:
    - "1s": Only use cached items less than 1 second old; fetch fresh data if cache
      is older
    - "1h": Only use cached items less than 1 hour old; fetch fresh data if cache is
      older
    - 0: Disable caching entirely; always fetch fresh data
    """

    clean_text: Annotated[bool, PropertyInfo(alias="cleanText")]
    """Whether to clean extracted text"""

    formats: List[Literal["text", "markdown"]]
    """Array of output formats to include in the response. Options: 'text', 'markdown'.

    - 'text': Extracted plain text (always available)
    - 'markdown': Markdown representation (only available for HTML content, empty
      string otherwise) Defaults to ['text'] if not specified.
    """

    headers: Dict[str, str]
    """Custom HTTP headers to send with the request (case-insensitive)"""

    max_redirects: Annotated[int, PropertyInfo(alias="maxRedirects")]
    """Maximum number of redirects to follow when fetching the URL.

    Must be between 0 (no redirects) and 20. Defaults to 5 if not specified.
    """

    max_size: Annotated[Union[int, str], PropertyInfo(alias="maxSize")]
    """Maximum content length for the URL response. Accepts either:

    - Integer: bytes (e.g., 8388608 for 8MB)
    - String: size format with unit (e.g., "1kb", "55mb", "1.2gb") Supported units:
      b (bytes), kb (kilobytes), mb (megabytes), gb (gigabytes), tb (terabytes) Must
      be between 1KB and 8MB. Defaults to "8mb" (8MB) if not specified.
    """

    max_timeout: Annotated[Union[int, str], PropertyInfo(alias="maxTimeout")]
    """Maximum time before the crawler gives up on loading a URL. Accepts either:

    - Integer: milliseconds (e.g., 15000 for 15 seconds)
    - String: time format with unit (e.g., "1s", "5h", "3m", "4.4h") Supported
      units: s (seconds), m (minutes), h (hours), d (days), ms (milliseconds) Must
      be between 1 second and 30 seconds. Defaults to "10s" (10 seconds) if not
      specified.
    """

    proxy: Proxy
    """Proxy configuration for the request"""

    stealth_mode: Annotated[bool, PropertyInfo(alias="stealthMode")]
    """When enabled, we use a proxy for the request.

    If set to true, and the 'proxy' option is set, it will be ignored. Defaults to
    false if not specified. Note: Enabling stealthMode consumes an additional
    credit/quota point (2 credits total instead of 1) for this request.
    """


class Proxy(TypedDict, total=False):
    """Proxy configuration for the request"""

    password: str
    """Proxy password for authentication"""

    server: str
    """
    Proxy server URL (e.g., http://proxy.example.com:8080 or
    socks5://proxy.example.com:1080)
    """

    username: str
    """Proxy username for authentication"""

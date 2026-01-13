# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, List, Union, Mapping, cast
from typing_extensions import Literal

import httpx

from ..types import extract_from_url_params, extract_from_file_params
from .._types import Body, Omit, Query, Headers, NotGiven, FileTypes, omit, not_given
from .._utils import extract_files, maybe_transform, deepcopy_minimal, async_maybe_transform
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from .._base_client import make_request_options
from ..types.extract_from_url_response import ExtractFromURLResponse
from ..types.extract_from_file_response import ExtractFromFileResponse

__all__ = ["ExtractResource", "AsyncExtractResource"]


class ExtractResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> ExtractResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/crawler-dot-dev/api-sdk-python#accessing-raw-response-data-eg-headers
        """
        return ExtractResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ExtractResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/crawler-dot-dev/api-sdk-python#with_streaming_response
        """
        return ExtractResourceWithStreamingResponse(self)

    def from_file(
        self,
        *,
        file: FileTypes,
        clean_text: bool | Omit = omit,
        formats: List[Literal["text", "markdown"]] | Omit = omit,
        max_timeout: Union[int, str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ExtractFromFileResponse:
        """Upload a file and extract text content from it.

        Supports PDF, DOC, DOCX, TXT and
        other text-extractable document formats.

        Args:
          file: The file to upload.

          clean_text:
              Whether to clean and normalize the extracted text. When enabled (true):

              - For HTML content: Removes script, style, and other non-text elements before
                extraction
              - Normalizes whitespace (collapses multiple spaces/tabs, normalizes newlines)
              - Removes empty lines and trims leading/trailing whitespace
              - Normalizes Unicode characters (NFC)
              - For JSON content: Only minimal cleaning to preserve structure When disabled
                (false): Returns raw extracted text without any processing.

          formats: Array of output formats to include in the response. Options: 'text', 'markdown'.

              - 'text': Extracted plain text (always available)
              - 'markdown': Markdown representation (only available for HTML content, empty
                string otherwise) Defaults to ['text'] if not specified.

          max_timeout:
              Maximum time before the file extraction gives up. Accepts either:

              - Integer: milliseconds (e.g., 30000 for 30 seconds)
              - String: time format with unit (e.g., "1s", "5h", "3m", "4.4h") Supported
                units: s (seconds), m (minutes), h (hours), d (days), ms (milliseconds) Must
                be between 5 seconds and 2 minutes. Defaults to "30s" (30 seconds) if not
                specified. This controls the timeout for Tika extraction operations on
                uploaded files.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        body = deepcopy_minimal(
            {
                "file": file,
                "clean_text": clean_text,
                "formats": formats,
                "max_timeout": max_timeout,
            }
        )
        files = extract_files(cast(Mapping[str, object], body), paths=[["file"]])
        # It should be noted that the actual Content-Type header that will be
        # sent to the server will contain a `boundary` parameter, e.g.
        # multipart/form-data; boundary=---abc--
        extra_headers = {"Content-Type": "multipart/form-data", **(extra_headers or {})}
        return self._post(
            "/v1/extract/file",
            body=maybe_transform(body, extract_from_file_params.ExtractFromFileParams),
            files=files,
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ExtractFromFileResponse,
        )

    def from_url(
        self,
        *,
        url: str,
        cache_age: Union[int, str] | Omit = omit,
        clean_text: bool | Omit = omit,
        formats: List[Literal["text", "markdown"]] | Omit = omit,
        headers: Dict[str, str] | Omit = omit,
        max_redirects: int | Omit = omit,
        max_size: Union[int, str] | Omit = omit,
        max_timeout: Union[int, str] | Omit = omit,
        proxy: extract_from_url_params.Proxy | Omit = omit,
        stealth_mode: bool | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ExtractFromURLResponse:
        """Extract text content from a webpage or document accessible via URL.

        Supports
        HTML, PDF, and other web-accessible content types.

        Args:
          url: The URL to extract text from.

          cache_age: Maximum acceptable age of cached content. This parameter controls how fresh
              cached data must be to be used.

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

          clean_text: Whether to clean extracted text

          formats: Array of output formats to include in the response. Options: 'text', 'markdown'.

              - 'text': Extracted plain text (always available)
              - 'markdown': Markdown representation (only available for HTML content, empty
                string otherwise) Defaults to ['text'] if not specified.

          headers: Custom HTTP headers to send with the request (case-insensitive)

          max_redirects: Maximum number of redirects to follow when fetching the URL. Must be between 0
              (no redirects) and 20. Defaults to 5 if not specified.

          max_size:
              Maximum content length for the URL response. Accepts either:

              - Integer: bytes (e.g., 8388608 for 8MB)
              - String: size format with unit (e.g., "1kb", "55mb", "1.2gb") Supported units:
                b (bytes), kb (kilobytes), mb (megabytes), gb (gigabytes), tb (terabytes) Must
                be between 1KB and 8MB. Defaults to "8mb" (8MB) if not specified.

          max_timeout:
              Maximum time before the crawler gives up on loading a URL. Accepts either:

              - Integer: milliseconds (e.g., 15000 for 15 seconds)
              - String: time format with unit (e.g., "1s", "5h", "3m", "4.4h") Supported
                units: s (seconds), m (minutes), h (hours), d (days), ms (milliseconds) Must
                be between 1 second and 30 seconds. Defaults to "10s" (10 seconds) if not
                specified.

          proxy: Proxy configuration for the request

          stealth_mode: When enabled, we use a proxy for the request. If set to true, and the 'proxy'
              option is set, it will be ignored. Defaults to false if not specified. Note:
              Enabling stealthMode consumes an additional credit/quota point (2 credits total
              instead of 1) for this request.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/v1/extract/url",
            body=maybe_transform(
                {
                    "url": url,
                    "cache_age": cache_age,
                    "clean_text": clean_text,
                    "formats": formats,
                    "headers": headers,
                    "max_redirects": max_redirects,
                    "max_size": max_size,
                    "max_timeout": max_timeout,
                    "proxy": proxy,
                    "stealth_mode": stealth_mode,
                },
                extract_from_url_params.ExtractFromURLParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ExtractFromURLResponse,
        )


class AsyncExtractResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncExtractResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/crawler-dot-dev/api-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AsyncExtractResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncExtractResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/crawler-dot-dev/api-sdk-python#with_streaming_response
        """
        return AsyncExtractResourceWithStreamingResponse(self)

    async def from_file(
        self,
        *,
        file: FileTypes,
        clean_text: bool | Omit = omit,
        formats: List[Literal["text", "markdown"]] | Omit = omit,
        max_timeout: Union[int, str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ExtractFromFileResponse:
        """Upload a file and extract text content from it.

        Supports PDF, DOC, DOCX, TXT and
        other text-extractable document formats.

        Args:
          file: The file to upload.

          clean_text:
              Whether to clean and normalize the extracted text. When enabled (true):

              - For HTML content: Removes script, style, and other non-text elements before
                extraction
              - Normalizes whitespace (collapses multiple spaces/tabs, normalizes newlines)
              - Removes empty lines and trims leading/trailing whitespace
              - Normalizes Unicode characters (NFC)
              - For JSON content: Only minimal cleaning to preserve structure When disabled
                (false): Returns raw extracted text without any processing.

          formats: Array of output formats to include in the response. Options: 'text', 'markdown'.

              - 'text': Extracted plain text (always available)
              - 'markdown': Markdown representation (only available for HTML content, empty
                string otherwise) Defaults to ['text'] if not specified.

          max_timeout:
              Maximum time before the file extraction gives up. Accepts either:

              - Integer: milliseconds (e.g., 30000 for 30 seconds)
              - String: time format with unit (e.g., "1s", "5h", "3m", "4.4h") Supported
                units: s (seconds), m (minutes), h (hours), d (days), ms (milliseconds) Must
                be between 5 seconds and 2 minutes. Defaults to "30s" (30 seconds) if not
                specified. This controls the timeout for Tika extraction operations on
                uploaded files.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        body = deepcopy_minimal(
            {
                "file": file,
                "clean_text": clean_text,
                "formats": formats,
                "max_timeout": max_timeout,
            }
        )
        files = extract_files(cast(Mapping[str, object], body), paths=[["file"]])
        # It should be noted that the actual Content-Type header that will be
        # sent to the server will contain a `boundary` parameter, e.g.
        # multipart/form-data; boundary=---abc--
        extra_headers = {"Content-Type": "multipart/form-data", **(extra_headers or {})}
        return await self._post(
            "/v1/extract/file",
            body=await async_maybe_transform(body, extract_from_file_params.ExtractFromFileParams),
            files=files,
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ExtractFromFileResponse,
        )

    async def from_url(
        self,
        *,
        url: str,
        cache_age: Union[int, str] | Omit = omit,
        clean_text: bool | Omit = omit,
        formats: List[Literal["text", "markdown"]] | Omit = omit,
        headers: Dict[str, str] | Omit = omit,
        max_redirects: int | Omit = omit,
        max_size: Union[int, str] | Omit = omit,
        max_timeout: Union[int, str] | Omit = omit,
        proxy: extract_from_url_params.Proxy | Omit = omit,
        stealth_mode: bool | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ExtractFromURLResponse:
        """Extract text content from a webpage or document accessible via URL.

        Supports
        HTML, PDF, and other web-accessible content types.

        Args:
          url: The URL to extract text from.

          cache_age: Maximum acceptable age of cached content. This parameter controls how fresh
              cached data must be to be used.

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

          clean_text: Whether to clean extracted text

          formats: Array of output formats to include in the response. Options: 'text', 'markdown'.

              - 'text': Extracted plain text (always available)
              - 'markdown': Markdown representation (only available for HTML content, empty
                string otherwise) Defaults to ['text'] if not specified.

          headers: Custom HTTP headers to send with the request (case-insensitive)

          max_redirects: Maximum number of redirects to follow when fetching the URL. Must be between 0
              (no redirects) and 20. Defaults to 5 if not specified.

          max_size:
              Maximum content length for the URL response. Accepts either:

              - Integer: bytes (e.g., 8388608 for 8MB)
              - String: size format with unit (e.g., "1kb", "55mb", "1.2gb") Supported units:
                b (bytes), kb (kilobytes), mb (megabytes), gb (gigabytes), tb (terabytes) Must
                be between 1KB and 8MB. Defaults to "8mb" (8MB) if not specified.

          max_timeout:
              Maximum time before the crawler gives up on loading a URL. Accepts either:

              - Integer: milliseconds (e.g., 15000 for 15 seconds)
              - String: time format with unit (e.g., "1s", "5h", "3m", "4.4h") Supported
                units: s (seconds), m (minutes), h (hours), d (days), ms (milliseconds) Must
                be between 1 second and 30 seconds. Defaults to "10s" (10 seconds) if not
                specified.

          proxy: Proxy configuration for the request

          stealth_mode: When enabled, we use a proxy for the request. If set to true, and the 'proxy'
              option is set, it will be ignored. Defaults to false if not specified. Note:
              Enabling stealthMode consumes an additional credit/quota point (2 credits total
              instead of 1) for this request.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/v1/extract/url",
            body=await async_maybe_transform(
                {
                    "url": url,
                    "cache_age": cache_age,
                    "clean_text": clean_text,
                    "formats": formats,
                    "headers": headers,
                    "max_redirects": max_redirects,
                    "max_size": max_size,
                    "max_timeout": max_timeout,
                    "proxy": proxy,
                    "stealth_mode": stealth_mode,
                },
                extract_from_url_params.ExtractFromURLParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ExtractFromURLResponse,
        )


class ExtractResourceWithRawResponse:
    def __init__(self, extract: ExtractResource) -> None:
        self._extract = extract

        self.from_file = to_raw_response_wrapper(
            extract.from_file,
        )
        self.from_url = to_raw_response_wrapper(
            extract.from_url,
        )


class AsyncExtractResourceWithRawResponse:
    def __init__(self, extract: AsyncExtractResource) -> None:
        self._extract = extract

        self.from_file = async_to_raw_response_wrapper(
            extract.from_file,
        )
        self.from_url = async_to_raw_response_wrapper(
            extract.from_url,
        )


class ExtractResourceWithStreamingResponse:
    def __init__(self, extract: ExtractResource) -> None:
        self._extract = extract

        self.from_file = to_streamed_response_wrapper(
            extract.from_file,
        )
        self.from_url = to_streamed_response_wrapper(
            extract.from_url,
        )


class AsyncExtractResourceWithStreamingResponse:
    def __init__(self, extract: AsyncExtractResource) -> None:
        self._extract = extract

        self.from_file = async_to_streamed_response_wrapper(
            extract.from_file,
        )
        self.from_url = async_to_streamed_response_wrapper(
            extract.from_url,
        )

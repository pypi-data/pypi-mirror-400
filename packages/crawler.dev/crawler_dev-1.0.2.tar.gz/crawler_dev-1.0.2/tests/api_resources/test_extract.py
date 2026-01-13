# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from api.crawler.dev_sdks import APICrawlerDevSDKs, AsyncAPICrawlerDevSDKs
from api.crawler.dev_sdks.types import (
    ExtractFromURLResponse,
    ExtractFromFileResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestExtract:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_from_file(self, client: APICrawlerDevSDKs) -> None:
        extract = client.extract.from_file(
            file=b"raw file contents",
        )
        assert_matches_type(ExtractFromFileResponse, extract, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_from_file_with_all_params(self, client: APICrawlerDevSDKs) -> None:
        extract = client.extract.from_file(
            file=b"raw file contents",
            clean_text=True,
            formats=["text", "markdown"],
            max_timeout="30s",
        )
        assert_matches_type(ExtractFromFileResponse, extract, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_from_file(self, client: APICrawlerDevSDKs) -> None:
        response = client.extract.with_raw_response.from_file(
            file=b"raw file contents",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        extract = response.parse()
        assert_matches_type(ExtractFromFileResponse, extract, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_from_file(self, client: APICrawlerDevSDKs) -> None:
        with client.extract.with_streaming_response.from_file(
            file=b"raw file contents",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            extract = response.parse()
            assert_matches_type(ExtractFromFileResponse, extract, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_from_url(self, client: APICrawlerDevSDKs) -> None:
        extract = client.extract.from_url(
            url="url",
        )
        assert_matches_type(ExtractFromURLResponse, extract, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_from_url_with_all_params(self, client: APICrawlerDevSDKs) -> None:
        extract = client.extract.from_url(
            url="url",
            cache_age="1d",
            clean_text=True,
            formats=["text", "markdown"],
            headers={
                "User-Agent": "Custom Bot/1.0",
                "X-API-Key": "my-api-key",
                "Accept-Language": "en-US",
            },
            max_redirects=5,
            max_size="8mb",
            max_timeout="15s",
            proxy={
                "password": "password",
                "server": "server",
                "username": "username",
            },
            stealth_mode=True,
        )
        assert_matches_type(ExtractFromURLResponse, extract, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_from_url(self, client: APICrawlerDevSDKs) -> None:
        response = client.extract.with_raw_response.from_url(
            url="url",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        extract = response.parse()
        assert_matches_type(ExtractFromURLResponse, extract, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_from_url(self, client: APICrawlerDevSDKs) -> None:
        with client.extract.with_streaming_response.from_url(
            url="url",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            extract = response.parse()
            assert_matches_type(ExtractFromURLResponse, extract, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncExtract:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_from_file(self, async_client: AsyncAPICrawlerDevSDKs) -> None:
        extract = await async_client.extract.from_file(
            file=b"raw file contents",
        )
        assert_matches_type(ExtractFromFileResponse, extract, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_from_file_with_all_params(self, async_client: AsyncAPICrawlerDevSDKs) -> None:
        extract = await async_client.extract.from_file(
            file=b"raw file contents",
            clean_text=True,
            formats=["text", "markdown"],
            max_timeout="30s",
        )
        assert_matches_type(ExtractFromFileResponse, extract, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_from_file(self, async_client: AsyncAPICrawlerDevSDKs) -> None:
        response = await async_client.extract.with_raw_response.from_file(
            file=b"raw file contents",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        extract = await response.parse()
        assert_matches_type(ExtractFromFileResponse, extract, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_from_file(self, async_client: AsyncAPICrawlerDevSDKs) -> None:
        async with async_client.extract.with_streaming_response.from_file(
            file=b"raw file contents",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            extract = await response.parse()
            assert_matches_type(ExtractFromFileResponse, extract, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_from_url(self, async_client: AsyncAPICrawlerDevSDKs) -> None:
        extract = await async_client.extract.from_url(
            url="url",
        )
        assert_matches_type(ExtractFromURLResponse, extract, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_from_url_with_all_params(self, async_client: AsyncAPICrawlerDevSDKs) -> None:
        extract = await async_client.extract.from_url(
            url="url",
            cache_age="1d",
            clean_text=True,
            formats=["text", "markdown"],
            headers={
                "User-Agent": "Custom Bot/1.0",
                "X-API-Key": "my-api-key",
                "Accept-Language": "en-US",
            },
            max_redirects=5,
            max_size="8mb",
            max_timeout="15s",
            proxy={
                "password": "password",
                "server": "server",
                "username": "username",
            },
            stealth_mode=True,
        )
        assert_matches_type(ExtractFromURLResponse, extract, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_from_url(self, async_client: AsyncAPICrawlerDevSDKs) -> None:
        response = await async_client.extract.with_raw_response.from_url(
            url="url",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        extract = await response.parse()
        assert_matches_type(ExtractFromURLResponse, extract, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_from_url(self, async_client: AsyncAPICrawlerDevSDKs) -> None:
        async with async_client.extract.with_streaming_response.from_url(
            url="url",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            extract = await response.parse()
            assert_matches_type(ExtractFromURLResponse, extract, path=["response"])

        assert cast(Any, response.is_closed) is True

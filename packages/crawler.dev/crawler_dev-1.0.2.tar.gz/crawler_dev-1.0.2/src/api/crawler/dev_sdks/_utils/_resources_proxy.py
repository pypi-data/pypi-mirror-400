from __future__ import annotations

from typing import Any
from typing_extensions import override

from ._proxy import LazyProxy


class ResourcesProxy(LazyProxy[Any]):
    """A proxy for the `api.crawler.dev_sdks.resources` module.

    This is used so that we can lazily import `api.crawler.dev_sdks.resources` only when
    needed *and* so that users can just import `api.crawler.dev_sdks` and reference `api.crawler.dev_sdks.resources`
    """

    @override
    def __load__(self) -> Any:
        import importlib

        mod = importlib.import_module("api.crawler.dev_sdks.resources")
        return mod


resources = ResourcesProxy().__as_proxied__()

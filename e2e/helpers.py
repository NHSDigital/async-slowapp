from types import TracebackType
from typing import Optional, Type, Any

import aiohttp
from aiohttp.typedefs import StrOrURL
from urllib.parse import urlparse
import os


class SessionClient:

    def __init__(self, base_uri, **kwargs):
        self.base_uri = base_uri
        self.session = aiohttp.ClientSession(**kwargs)

    async def __aenter__(self) -> "SessionClient":
        return self

    def _full_url(self, url: StrOrURL) -> StrOrURL:
        if type(url) != str:
            return url

        parsed = urlparse(url)
        if parsed.scheme:
            return url

        url = os.path.join(self.base_uri, url)
        return url

    def get(self, url: StrOrURL, *, allow_redirects: bool = True, **kwargs: Any) -> "aoihttp._RequestContextManager":
        uri = self._full_url(url)
        return self.session.get(uri, allow_redirects=allow_redirects, **kwargs)

    async def close(self):
        await self.session.close()
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        await self.close()


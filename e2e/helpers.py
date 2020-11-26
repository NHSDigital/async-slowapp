from types import TracebackType
from typing import Optional, Type, Any

import aiohttp
from aiohttp.typedefs import StrOrURL
from urllib.parse import urlparse, urljoin
import os

from dataclasses import dataclass, field


@dataclass(frozen=True)
class TestSessionConfig:
    api_environment: Optional[str] = field(default=None)
    service_base_path: Optional[str] = field(default=None)
    api_host: str = field(init=False)
    base_uri: str = field(init=False)

    def __post_init__(self):
        if not self.api_environment:
            object.__setattr__(self, "api_environment", os.environ.get('APIGEE_ENVIRONMENT', 'internal-dev'))

        if not self.service_base_path:
            object.__setattr__(self, "service_base_path", os.environ.get('SERVICE_BASE_PATH', 'async-slowapp-pr-1'))

        apis_base = 'api.service.nhs.uk'
        api_host = apis_base if self.api_environment == 'prod' else f'{self.api_environment}.{apis_base}'
        base_uri = urljoin(f"https://{api_host}", self.service_base_path)
        object.__setattr__(self, 'api_host', api_host)
        object.__setattr__(self, 'base_uri', base_uri)


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


import pytest
from aiohttp import ClientResponse
from api_test_utils import poll_until
from api_test_utils.api_session_client import APISessionClient
from api_test_utils.api_test_session_config import APITestSessionConfig


@pytest.mark.smoketest
@pytest.mark.asyncio
async def test_wait_for_ping(api_client: APISessionClient, api_test_config: APITestSessionConfig):

    async def _is_complete(resp: ClientResponse):

        if resp.status != 200:
            return False
        body = await resp.json()
        return body.get("commitId") == api_test_config.commit_id

    await poll_until(
        make_request=lambda: api_client.get('_ping'),
        until=_is_complete,
        timeout=120
    )


@pytest.mark.smoketest
@pytest.mark.asyncio
async def test_wait_for_status(api_client: APISessionClient, api_test_config: APITestSessionConfig):

    async def _is_complete(resp: ClientResponse):

        if resp.status != 200:
            return False
        body = await resp.json()
        version_info = body.get('_version')
        if not version_info:
            return False

        return version_info.get("commitId") == api_test_config.commit_id

    await poll_until(
        make_request=lambda: api_client.get('_status'),
        until=_is_complete,
        timeout=120
    )


@pytest.mark.smoketest
@pytest.mark.asyncio
async def test_api_status_with_service_header_another_service(api_client: APISessionClient):

    async with api_client.get("_status", headers={'x-apim-service': 'sync-wrap'}) as r:
        assert r.status == 200, (r.status, r.reason, (await r.text())[:2000])
        body = await r.json()

        assert body.get("service") == 'async-slowapp'


@pytest.mark.smoketest
@pytest.mark.asyncio
async def test_api_status_with_service_header(api_client: APISessionClient):

    async with api_client.get("_status", headers={'x-apim-service': 'async-slowapp'}) as r:
        assert r.status == 200, (r.status, r.reason, (await r.text())[:2000])
        body = await r.json()

        assert body.get("service") == 'async-slowapp'


@pytest.mark.asyncio
async def test_api_poll_with_missing_id(api_client: APISessionClient):

    async with api_client.get("poll?id=madeup") as r:
        assert r.status == 404, (r.status, r.reason, (await r.text())[:2000])


@pytest.mark.asyncio
async def test_api_delete_poll_with_missing_id(api_client: APISessionClient):

    async with api_client.delete("poll?id=madeup") as r:
        assert r.status == 404, (r.status, r.reason, (await r.text())[:2000])


@pytest.mark.asyncio
async def test_api_slow_supplies_content_location(api_client: APISessionClient, api_test_config: APITestSessionConfig):

    async with api_client.get("slow") as r:
        assert r.status == 202, (r.status, r.reason, (await r.text())[:2000])
        assert r.headers.get('Content-Type') == 'application/json'
        assert r.headers.get('Content-Location').startswith(api_test_config.base_uri + '/poll?')
        assert r.cookies.get('poll-count') == '0'


@pytest.mark.asyncio
async def test_api_slow_supplies_content_location(api_client: APISessionClient):

    async with api_client.get("slow?complete_in=0.01&final_status=418") as r:

        assert 'application/json' in r.headers.get('Content-Type')
        poll_location = r.headers.get('Content-Location')
        assert r.status == 202, (r.status, r.reason, (await r.text())[:2000])

    async with api_client.get(poll_location) as r:
        poll_count = r.cookies.get('poll-count')
        assert poll_count.value == '1'
        assert r.status == 418, (r.status, r.reason, (await r.text())[:2000])

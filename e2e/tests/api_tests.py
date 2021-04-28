import asyncio
from typing import List

import pytest
from aiohttp import ClientResponse
from api_test_utils import poll_until
from api_test_utils.api_session_client import APISessionClient
from api_test_utils.api_test_session_config import APITestSessionConfig
from api_test_utils import env


def dict_path(raw, path: List[str]):
    if not raw:
        return raw

    if not path:
        return raw

    res = raw.get(path[0])
    if not res or len(path) == 1 or type(res) != dict:
        return res

    return dict_path(res, path[1:])


@pytest.mark.e2e
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


@pytest.mark.e2e
@pytest.mark.smoketest
@pytest.mark.asyncio
async def test_check_status_is_secured(api_client: APISessionClient):

    async with api_client.get("_status", allow_retries=True) as resp:
        assert resp.status == 401


@pytest.mark.e2e
@pytest.mark.smoketest
@pytest.mark.asyncio
async def test_wait_for_status(
        api_client: APISessionClient, api_test_config: APITestSessionConfig
):
    async def is_deployed(resp: ClientResponse):
        if resp.status != 200:
            return False
        body = await resp.json()

        if body.get("commitId") != api_test_config.commit_id:
            return False

        backend = dict_path(body, ["checks", "healthcheck", "outcome", "version"])

        if type(backend) != dict:
            return False

        return backend.get("commitId") == api_test_config.commit_id

    await poll_until(
        make_request=lambda: api_client.get(
            "_status", headers={"apikey": env.status_endpoint_api_key()}
        ),
        until=is_deployed,
        timeout=120,
    )


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_api_status_with_service_header_another_service(api_client: APISessionClient):

    r = await api_client.get(
        "_status", allow_retries=True, max_retries=5,
        headers={
            'x-apim-service': 'async-slowapp',
            'apikey': env.status_endpoint_api_key()
        }
    )
    assert r.status == 200, (r.status, r.reason, (await r.text())[:2000])
    body = await r.json()

    service = dict_path(body, ["checks", "healthcheck", "outcome", "service"])

    assert service == 'async-slowapp'


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_api_status_with_service_header(api_client: APISessionClient):

    r = await api_client.get(
        "_status", allow_retries=True, max_retries=5,
        headers={
            'x-apim-service': 'sync-wrap',
            'apikey': env.status_endpoint_api_key()
        }
    )
    assert r.status == 200, (r.status, r.reason, (await r.text())[:2000])
    body = await r.json()

    service = dict_path(body, ["checks", "healthcheck", "outcome", "service"])

    assert service == 'async-slowapp'


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_api_poll_with_missing_id(api_client: APISessionClient):

    async with api_client.get("poll?id=madeup") as r:
        assert r.status == 404, (r.status, r.reason, (await r.text())[:2000])


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_api_delete_poll_with_missing_id(api_client: APISessionClient):

    async with api_client.delete("poll?id=madeup") as r:
        assert r.status == 404, (r.status, r.reason, (await r.text())[:2000])


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_api_slow_supplies_content_location(api_client: APISessionClient, api_test_config: APITestSessionConfig):

    async with api_client.get("slow") as r:
        assert r.status == 202, (r.status, r.reason, (await r.text())[:2000])
        assert r.headers.get('Content-Type') == 'application/json'
        assert r.headers.get('Content-Location').startswith(api_test_config.base_uri + '/poll?')
        assert r.cookies.get('poll-count') == '0'


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_api_slow_supplies_content_location(api_client: APISessionClient):

    async with api_client.get("slow?complete_in=0.1&final_status=418") as r:

        assert 'application/json' in r.headers.get('Content-Type')
        poll_location = r.headers.get('Content-Location')
        poll_count = r.cookies.get('poll-count')
        assert poll_count.value == '0'
        assert r.status == 202, (r.status, r.reason, (await r.text())[:2000])

    async with api_client.get(poll_location, cookies={'poll-count': '0'}) as r:
        poll_count = r.cookies.get('poll-count')
        assert poll_count.value == '1'
        assert r.status == 202, (r.status, r.reason, (await r.text())[:2000])

    await asyncio.sleep(0.1)

    async with api_client.get(poll_location, cookies={'poll-count': '1'}) as r:
        poll_count = r.cookies.get('poll-count')
        assert poll_count.value == '2'
        assert r.status == 418, (r.status, r.reason, (await r.text())[:2000])

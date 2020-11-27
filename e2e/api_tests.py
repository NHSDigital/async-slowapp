import pytest
from helpers import SessionClient, TestSessionConfig


@pytest.mark.asyncio
async def test_postman_echo_read_multivalue_headers():
    async with SessionClient("http://postman-echo.com") as session:
        async with session.get("response-headers?foo1=bar1&foo1=bar2") as resp:
            bars = resp.headers.getall('foo1')
            assert bars == ['bar1', 'bar2']


@pytest.mark.asyncio
async def test_postman_echo_send_multivalue_headers():
    async with SessionClient("http://postman-echo.com") as session:
        async with session.get("headers", headers=[("foo1", "bar1"), ("foo1", "bar2")]) as r:
            body = await r.json()

            assert body["headers"]["foo1"] == "bar1, bar2"


@pytest.mark.asyncio
async def test_api_status(api: SessionClient):

    async with api.get("_status") as r:
        assert r.status == 200
        body = await r.json()

        assert body == dict(ping='pong', service='async-slowapp')


@pytest.mark.asyncio
async def test_app_ping(api: SessionClient, test_config: TestSessionConfig):

    async with api.get("_ping") as r:
        assert r.status == 200
        body = await r.json()

        assert body["version"] == test_config.service_base_path


@pytest.mark.asyncio
async def test_api_status_with_service_header(api: SessionClient):

    async with api.get("_status", headers={'x-apim-service': 'sync-wrap'}) as r:
        assert r.status == 200
        body = await r.json()

        assert body == dict(ping='pong', service='async-slowapp')


@pytest.mark.asyncio
async def test_api_poll_with_missing_id(api: SessionClient):

    async with api.get("poll?id=madeup") as r:
        assert r.status == 404


@pytest.mark.asyncio
async def test_api_delete_poll_with_missing_id(api: SessionClient):

    async with api.delete("poll?id=madeup") as r:
        assert r.status == 404


@pytest.mark.asyncio
async def test_api_slow_supplies_content_location(api: SessionClient, test_config: TestSessionConfig):

    async with api.get("slow") as r:
        assert r.status == 202
        assert r.headers.get('Content-Type') == 'application/json'
        assert r.headers.get('Content-Location').startswith(test_config.base_uri + '/poll?')
        assert r.cookies.get('poll-count') == '0'


@pytest.mark.asyncio
async def test_api_slow_supplies_content_location(api: SessionClient):

    async with api.get("slow?complete_in=0.01&final_status=418") as r:

        assert 'application/json' in r.headers.get('Content-Type')
        poll_location = r.headers.get('Content-Location')
        assert r.status == 202

    async with api.get(poll_location) as r:
        poll_count = r.cookies.get('poll-count')
        assert poll_count.value == '1'
        assert r.status == 418

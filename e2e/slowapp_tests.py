import http.client
from collections import defaultdict


import aiohttp
import pytest


#
# def test_postman_echo_basic_status():
#
#     conn = http.client.HTTPSConnection("postman-echo.com")
#     conn.request("GET", "/status/408")
#     resp = conn.getresponse()
#
#     assert resp.status == 408
#
from helpers import SessionClient


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
async def test_app_ping(api: SessionClient):

    async with api.get("_ping") as r:
        assert r.status == 200
        body = await r.json()

        assert body == ''


@pytest.mark.asyncio
async def test_api_status(api: SessionClient):

    async with api.get("_status") as r:
        assert r.status == 200
        body = await r.json()

        assert body == dict(ping='pong', service='async-slowapp')


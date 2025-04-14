from os import getenv
from time import sleep
from typing import List

import pytest
import requests


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
def test_wait_for_ping(nhsd_apim_proxy_url):
    retries = 0
    resp = requests.get(f"{nhsd_apim_proxy_url}/_ping", timeout=30)
    deployed_commit_id = resp.json().get("commitId")

    while deployed_commit_id != getenv("SOURCE_COMMIT_ID") and retries <= 30:
        resp = requests.get(f"{nhsd_apim_proxy_url}/_ping", timeout=30)

        if resp.status_code != 200:
            pytest.fail(f"Status code {resp.status_code}, expecting 200")

        deployed_commit_id = resp.json().get("commitId")
        retries += 1
        sleep(1)

    if retries >= 30:
        pytest.fail("Timeout Error - max retries")

    assert deployed_commit_id == getenv("SOURCE_COMMIT_ID")


@pytest.mark.e2e
@pytest.mark.smoketest
def test_check_status_is_secured(nhsd_apim_proxy_url):
    resp = requests.get(f"{nhsd_apim_proxy_url}/_status")
    assert resp.status_code == 401


@pytest.mark.e2e
@pytest.mark.smoketest
@pytest.mark.parametrize("service_header", ["", "async-slowapp", "sync-wrap"])
def test_wait_for_status(nhsd_apim_proxy_url, status_endpoint_auth_headers, service_header):
    def _container_not_ready(resp: requests.Response):
        """
        Requests to ECS containers which are still starting up return with a
        HTTP 503 (service unavailable).
        """
        return resp.json().get("checks", {}) \
            .get("healthcheck", {}) \
            .get("responseCode") == 503

    retries = 0
    headers = status_endpoint_auth_headers
    if service_header:
        headers["x-apim-service"] = service_header
    resp = requests.get(
        f"{nhsd_apim_proxy_url}/_status", headers=headers, timeout=30
    )

    if resp.status_code != 200:
        # Status should always be 200 we don't need to wait for it
        pytest.fail(f"Status code {resp.status_code}, expecting 200")
    if not resp.json().get("version"):
        pytest.fail("version not found")

    deployed_commit_id = resp.json().get("commitId")

    while deployed_commit_id != getenv("SOURCE_COMMIT_ID") or _container_not_ready(resp) and retries <= 50:
        resp = requests.get(
            f"{nhsd_apim_proxy_url}/_status", headers=status_endpoint_auth_headers, timeout=30
        )

        deployed_commit_id = resp.json().get("commitId")
        retries += 1
        sleep(1)

    if retries >= 45:
        pytest.fail("Timeout Error - max retries")

    body = resp.json()
    assert body.get("status") == "pass"

    service = dict_path(body, ["checks", "healthcheck", "outcome", "service"])
    assert service == 'async-slowapp'


@pytest.mark.e2e
def test_api_poll_with_missing_id(nhsd_apim_proxy_url):
    resp = requests.get(f"{nhsd_apim_proxy_url}/poll?id=madeup")
    assert resp.status_code == 404, (resp.status_code, resp.reason, resp.text[:2000])


@pytest.mark.e2e
def test_api_delete_poll_with_missing_id(nhsd_apim_proxy_url):
    resp = requests.delete(f"{nhsd_apim_proxy_url}/poll?id=madeup")
    assert resp.status_code == 404, (resp.status_code, resp.reason, resp.text[:2000])


@pytest.mark.e2e
def test_api_slow_supplies_content_location(nhsd_apim_proxy_url):
    resp = requests.get(f"{nhsd_apim_proxy_url}/slow")
    assert resp.status_code == 202, (resp.status_code, resp.reason, resp.text[:2000])
    assert 'application/json' in resp.headers.get('Content-Type')
    assert resp.headers.get('Content-Location').startswith(nhsd_apim_proxy_url + '/poll?')
    assert resp.cookies.get('poll-count') == '0'


@pytest.mark.e2e
def test_api_slow_test_final_status(nhsd_apim_proxy_url):
    resp = requests.get(f"{nhsd_apim_proxy_url}/slow?complete_in=0.1&final_status=418")
    assert 'application/json' in resp.headers.get('Content-Type')
    poll_location = resp.headers.get('Content-Location')
    poll_count = resp.cookies.get('poll-count')
    assert poll_count == '0'
    assert resp.status_code == 202, (resp.status_code, resp.reason, resp.text[:2000])

    resp = requests.get(poll_location, cookies={'poll-count': '0'})
    poll_count = resp.cookies.get('poll-count')
    assert poll_count == '1'
    assert resp.status_code == 202, (resp.status_code, resp.reason, resp.text[:2000])

    sleep(0.5)

    resp = requests.get(poll_location, cookies={'poll-count': '1'})
    poll_count = resp.cookies.get('poll-count')
    assert poll_count == '2'
    assert resp.status_code == 418, (resp.status_code, resp.reason, resp.text[:2000])

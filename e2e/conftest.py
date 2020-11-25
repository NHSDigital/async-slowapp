import pytest
import os
from helpers import SessionClient
from urllib.parse import urljoin


@pytest.fixture(scope='function')
async def api():
    apis_base = 'api.service.nhs.uk'
    apigee_env = os.environ.get('APIGEE_ENVIRONMENT', 'internal-dev')
    host = apis_base if apigee_env == 'prod' else f'{apigee_env}.api.service.nhs.uk'
    base_path = os.environ.get('SERVICE_BASE_PATH', 'async-slowapp')

    session_client = SessionClient(urljoin(f"https://{host}", base_path))

    yield session_client

    await session_client.close()

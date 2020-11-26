import pytest
from helpers import SessionClient, TestSessionConfig


@pytest.fixture(scope='session')
def test_config() -> TestSessionConfig:

    return TestSessionConfig()


@pytest.fixture(scope='function')
async def api(test_config: TestSessionConfig):

    session_client = SessionClient(test_config.base_uri)

    yield session_client

    await session_client.close()

import pytest
from pydantic_settings import BaseSettings, SettingsConfigDict

from wattmaven_solarnetwork_tools.core.solarnetwork_client import (
    SolarNetworkCredentials,
)


class Settings(BaseSettings):
    """
    Settings for the tests.
    """

    solarnetwork_host: str
    solarnetwork_token: str
    solarnetwork_secret: str
    solarnetwork_test_node_id: str

    model_config: SettingsConfigDict = SettingsConfigDict(env_file=".env")


settings = Settings()


@pytest.fixture
def credentials():
    return SolarNetworkCredentials(
        token=settings.solarnetwork_token,
        secret=settings.solarnetwork_secret,
        host=settings.solarnetwork_host,
    )


@pytest.fixture
def test_node_id():
    return settings.solarnetwork_test_node_id

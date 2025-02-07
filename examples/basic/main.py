"""
Example of how to use the SolarNetworkClient.
"""

from settings import settings

from wattmaven_solarnetwork_tools.core.solarnetwork_client import (
    SolarNetworkClient,
    SolarNetworkCredentials,
)


def get_nodes() -> list[int]:
    """
    Get all nodes from the SolarNetwork API.

    Returns:
        list[int]: A list of node IDs.
    """
    with SolarNetworkClient(
        SolarNetworkCredentials(
            token=settings.solarnetwork_token,
            secret=settings.solarnetwork_secret,
            host=settings.solarnetwork_host,
        )
    ) as client:
        response = client.request("GET", "/solarquery/api/v1/sec/nodes")
        json = response.json()
        return json["data"]


def main():
    nodes = get_nodes()
    print(nodes)


if __name__ == "__main__":
    main()

import pytest

from wattmaven_solarnetwork_tools.core.solarnetwork_client import (
    SolarNetworkClient,
    SolarNetworkCredentials,
)


@pytest.mark.integration
class TestSolarNetworkClient:
    def test_get_nodes_with_valid_credentials(self, credentials):
        with SolarNetworkClient(credentials) as client:
            response = client.request("GET", "/solarquery/api/v1/sec/nodes")
            assert response.status_code == 200
            assert response.json()["success"] is True

    def test_get_nodes_with_invalid_credentials(self, credentials):
        invalid_credentials = SolarNetworkCredentials(
            token="invalid-token", secret="invalid-secret", host=credentials.host
        )

        with SolarNetworkClient(invalid_credentials) as client:
            response = client.request("GET", "/solarquery/api/v1/sec/nodes")
            assert response.status_code == 403
            assert response.json()["success"] is False

    def test_get_datum_list_with_random_order_of_parameters(
        self, credentials, test_node_id
    ):
        with SolarNetworkClient(credentials) as client:
            response = client.request(
                "GET",
                "/solarquery/api/v1/sec/datum/list",
                # Should be able to handle parameters that _aren't_ in alphabetical order.
                params={
                    "nodeId": test_node_id,
                    "startDate": "2025-01-07",
                    "endDate": "2025-01-01",
                    "aggregation": "Day",
                },
            )
            assert response.status_code == 200
            assert response.json()["success"] is True

    def test_get_datum_list_with_source_id(self, credentials, test_node_id):
        with SolarNetworkClient(credentials) as client:
            response = client.request(
                "GET",
                "/solarquery/api/v1/sec/datum/list",
                params={
                    "nodeId": test_node_id,
                    # Source IDs are good to test because they must be correctly encoded.
                    "sourceId": "*/**",
                    "startDate": "2025-01-07",
                    "endDate": "2025-01-01",
                    "aggregation": "Day",
                },
            )
            assert response.status_code == 200
            assert response.json()["success"] is True

    def test_get_datum_list_with_accept_header(self, credentials, test_node_id):
        with SolarNetworkClient(credentials) as client:
            response = client.request(
                "GET",
                "/solarquery/api/v1/sec/datum/list",
                params={
                    "nodeId": test_node_id,
                    "startDate": "2025-01-07",
                    "endDate": "2025-01-01",
                    "aggregation": "Day",
                },
                accept="text/csv",
            )
            assert response.status_code == 200
            assert response.headers["Content-Type"].startswith("text/csv")

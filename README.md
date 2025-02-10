# `wattmaven-solarnetwork-tools`

The WattMaven SolarNetwork tools.

## Installation

```bash
pip install wattmaven-solarnetwork-tools
```

## Usage

See [examples](./examples) for usage examples.

```python
from wattmaven_solarnetwork_tools.core.solarnetwork_client import (
    SolarNetworkClient,
    SolarNetworkCredentials,
)

# Create a client
with SolarNetworkClient(
    credentials=SolarNetworkCredentials(
        token="your_token",
        secret="your_secret",
    )
) as client:
    # Make requests
    response = client.request("GET", "/solarquery/api/v1/sec/nodes")
    json = response.json()
    print(json)
    # ...
```

## License

This project is licensed under the **MIT License**. See the [LICENSE](./LICENSE) file for details.

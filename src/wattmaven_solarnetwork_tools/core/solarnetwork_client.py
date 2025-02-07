import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from urllib.parse import urlencode

import requests

from wattmaven_solarnetwork_tools.core.authentication import (
    generate_auth_header,
    get_x_sn_date,
)


@dataclass
class SolarNetworkCredentials:
    """Credentials for authenticating with SolarNetwork."""

    token: str
    secret: str
    host: str = "data.solarnetwork.net"


class SolarNetworkClient:
    """Client for interacting with the SolarNetwork API."""

    def __init__(self, credentials: SolarNetworkCredentials):
        """
        Initialize the SolarNetwork client.

        Args:
            credentials: SolarNetwork authentication credentials
        """
        self.credentials = credentials
        self._session = requests.Session()

    def _prepare_request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        accept: Optional[str] = "application/json",
    ) -> requests.Request:
        """Prepare a request with authentication headers.

        Args:
            method: HTTP method
            path: API endpoint path
            params: Query parameters
            data: Request body data
            accept: Accept header value, defaults to application/json

        Returns:
            Prepared request
        """
        now = datetime.now(timezone.utc)
        date = get_x_sn_date(now)

        headers = {
            "accept": accept,
            "host": self.credentials.host,
            "x-sn-date": date,
        }

        # Generate auth header
        auth = generate_auth_header(
            self.credentials.token,
            self.credentials.secret,
            method,
            path,
            urlencode(params) if params else "",
            headers,
            json.dumps(data) if data else "",
            now,
        )
        headers["Authorization"] = auth

        if isinstance(data, dict):
            headers["Content-Type"] = "application/json"

        return requests.Request(
            method=method,
            url=f"https://{self.credentials.host}{path}",
            params=params,
            headers=headers,
            json=data if isinstance(data, dict) else None,
        )

    def request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        accept: Optional[str] = "application/json",
    ) -> requests.Response:
        """
        Make an authenticated request to the SolarNetwork API.

        Args:
            method: HTTP method
            path: API endpoint path
            params: Query parameters
            data: Request body data
            accept: Accept header value, defaults to application/json
        Returns:
            API response
        """
        request = self._prepare_request(method, path, params, data, accept)
        prepared = request.prepare()
        return self._session.send(prepared)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._session.close()

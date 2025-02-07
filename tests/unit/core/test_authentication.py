from datetime import datetime, timezone

import pytest

from wattmaven_solarnetwork_tools.core.authentication import (
    generate_auth_header,
    generate_canonical_request_message,
    generate_signing_key_hex,
    generate_signing_message,
    get_x_sn_date,
    order_query_parameters,
)


@pytest.mark.unit
def test_get_x_sn_date():
    # Test with a specific datetime
    dt = datetime(2024, 2, 4, 12, 30, 45, tzinfo=timezone.utc)
    expected = "Sun, 04 Feb 2024 12:30:45 GMT"
    assert get_x_sn_date(dt) == expected


@pytest.mark.unit
def test_generate_signing_key_hex():
    dt = datetime(2024, 2, 4, 12, 30, 45, tzinfo=timezone.utc)
    secret = "test_secret"
    request = "snws2_request"

    # The result should be a 64-character hex string
    result = generate_signing_key_hex(secret, dt, request)
    assert isinstance(result, str)
    assert len(result) == 64
    # Verify it's a valid hex string
    int(result, 16)  # This will raise ValueError if not valid hex


@pytest.mark.unit
def test_order_query_parameters():
    # Test empty string
    assert order_query_parameters("") == ""

    # Test single parameter
    assert order_query_parameters("foo=1") == "foo=1"

    # Test multiple parameters
    assert order_query_parameters("foo=1&bar=2") == "bar=2&foo=1"

    # Test multiple parameters with same key
    assert order_query_parameters("foo=1&bar=2&foo=3") == "bar=2&foo=1&foo=3"


@pytest.mark.unit
def test_generate_canonical_request_message():
    method = "GET"
    path = "/api/v1/data"
    parameters = "foo=1&bar=2"
    signed_headers = {
        "host": "api.example.com",
        "x-sn-date": "Sun, 04 Feb 2024 12:30:45 GMT",
    }
    body = ""

    result = generate_canonical_request_message(
        method, path, parameters, signed_headers, body
    )

    expected_lines = [
        "GET",
        "/api/v1/data",
        "bar=2&foo=1",
        "host:api.example.com",
        "x-sn-date:Sun, 04 Feb 2024 12:30:45 GMT",
        "host;x-sn-date",
        "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",  # SHA256 of empty string
    ]
    expected = "\n".join(expected_lines)

    assert result == expected


@pytest.mark.unit
def test_generate_signing_message():
    dt = datetime(2024, 2, 4, 12, 30, 45, tzinfo=timezone.utc)
    canonical_request = "GET\n/api/v1/data\nbar=2&foo=1\nhost:api.example.com\nx-sn-date:Sun, 04 Feb 2024 12:30:45 GMT\nhost;x-sn-date\ne3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"

    result = generate_signing_message(dt, canonical_request)

    # Verify structure of the message
    lines = result.split("\n")
    assert len(lines) == 3
    assert lines[0] == "SNWS2-HMAC-SHA256"
    assert lines[1] == "20240204T123045Z"
    # Third line should be a 64-character hex string (SHA256 hash)
    assert len(lines[2]) == 64
    int(lines[2], 16)  # Verify it's valid hex


@pytest.mark.unit
def test_generate_auth_header():
    dt = datetime(2024, 2, 4, 12, 30, 45, tzinfo=timezone.utc)
    token = "test_token"
    secret = "test_secret"
    method = "GET"
    path = "/api/v1/data"
    params = "foo=1&bar=2"
    signed_headers = {
        "host": "api.example.com",
        "x-sn-date": "Sun, 04 Feb 2024 12:30:45 GMT",
    }
    body = ""

    result = generate_auth_header(
        token, secret, method, path, params, signed_headers, body, dt
    )

    # Verify structure of auth header
    assert result.startswith("SNWS2 Credential=test_token,SignedHeaders=")
    assert "host;x-sn-date" in result
    assert ",Signature=" in result

    # Extract and verify signature
    signature = result.split(",Signature=")[1]
    assert len(signature) == 64
    int(signature, 16)  # Verify it's valid hex


@pytest.mark.unit
@pytest.mark.parametrize(
    "test_input,expected",
    [
        # Empty string
        ("", ""),
        # Single parameter
        ("foo=1", "foo=1"),
        # Multiple parameters
        ("foo=1&bar=2", "bar=2&foo=1"),
        # Duplicate keys
        ("foo=1&bar=2&foo=3", "bar=2&foo=1&foo=3"),
        # Multiple values with same key
        ("x=1&x=2&x=3", "x=1&x=2&x=3"),
    ],
)
def test_order_query_parameters_parametrize(test_input, expected):
    assert order_query_parameters(test_input) == expected

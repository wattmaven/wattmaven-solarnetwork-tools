# See https://github.com/SolarNetwork/solarnetwork/wiki/SolarNet-API-authentication-scheme-V2

import datetime
import hashlib
import hmac
from urllib.parse import parse_qs, quote_plus, urlencode


def get_x_sn_date(dt: datetime.datetime) -> str:
    """
    Get the X-SN-Date header value for the given datetime.

    Args:
        dt: The datetime to use for the X-SN-Date header value.

    Returns:
        The X-SN-Date header value.
    """
    # Format the given datetime to the following example format:
    # Fri, 03 Mar 2017 04:36:28 GMT
    return dt.strftime("%a, %d %b %Y %H:%M:%S GMT")


def hmac_sha256(secret: bytes, content: bytes) -> hmac.HMAC:
    """
    Generate an HMAC SHA-256 signature for the given secret and content.

    Args:
        secret: The secret to use for the HMAC SHA-256 signature.
        content: The content to use for the HMAC SHA-256 signature.

    Returns:
        The HMAC SHA-256 signature.
    """
    signature = hmac.new(secret, content, digestmod=hashlib.sha256)
    return signature


def generate_signing_key(secret: str, dt: datetime.datetime, request: str) -> bytes:
    """
    Generate a signing key for the given secret, datetime, and request.

    Args:
        secret: The secret to use for the signing key.
        dt: The datetime to use for the signing key.
        request: The request to use for the signing key.

    Returns:
        The signing key.
    """
    date = dt.strftime("%Y%m%d")
    inner_secret = f"SNWS2{secret}"

    inner = hmac_sha256(bytes(inner_secret, "latin-1"), bytes(date, "latin-1"))
    outer = hmac_sha256(inner.digest(), bytes(request, "latin-1"))

    return outer.digest()


def generate_signing_key_hex(secret: str, dt: datetime.datetime, request: str) -> str:
    """
    Generate a signing key for the given secret, datetime, and request.

    Args:
        secret: The secret to use for the signing key.
        dt: The datetime to use for the signing key.
        request: The request to use for the signing key.

    Returns:
        The signing key.
    """
    return generate_signing_key(secret, dt, request).hex()


def generate_signing_message(
    dt: datetime.datetime, canonical_request_message: str
) -> str:
    """
    Generate the signing message for the given datetime and canonical request message.

    Args:
        dt: The datetime to use for the signing message.
        canonical_request_message: The canonical request message to use for the signing message.

    Returns:
        The signing message.
    """
    # The final message to sign is 3 lines of data delimited by a newline character:
    # * The literal string SNWS2-HMAC-SHA256
    # * The request date, formatted as an UTC ISO8601 timestamp like YYYYMMDD'T'HHmmss'Z'
    # * The Hex(SHA256(CanonicalRequestMessage)) where CanonicalRequestMessage is the canonical request message string as described in the previous section.
    #         For example, the signing message for a request might look like:
    #
    # SNWS2-HMAC-SHA256
    # 20170303T043628Z
    # 8f732085380ed6dc18d8556a96c58c820b0148852a61b3c828cb9cfd233ae05f
    digest = hashlib.sha256(bytes(canonical_request_message, "latin-1")).hexdigest()
    output = f"SNWS2-HMAC-SHA256\n{dt.strftime('%Y%m%dT%H%M%SZ')}\n{digest}"

    return output


def order_query_parameters(query_string: str) -> str:
    """
    Orders query parameters alphabetically by key.

    Args:
        query_string: The query string to order (e.g. 'foo=1&bar=2')

    Returns:
        An ordered query string with parameters sorted by key

    Example:
        >>> order_query_parameters('foo=1&bar=2&baz=3')
        'bar=2&baz=3&foo=1'
    """
    # Handle empty string case
    if not query_string:
        return ""

    # Parse the query string into a dict
    params = parse_qs(query_string)

    # Convert the dict to list of tuples and sort by key
    # Note: parse_qs returns values as lists, so we take first value if only one exists
    ordered_params = []
    for key in sorted(params.keys()):
        values = params[key]
        if len(values) == 1:
            ordered_params.append((key, values[0]))
        else:
            # If multiple values exist for a key, they should maintain their order
            for value in values:
                ordered_params.append((key, value))

    # Convert back to query string
    return urlencode(ordered_params, safe="", quote_via=quote_plus)


def generate_canonical_request_message(
    method: str, path: str, parameters: str, signed_headers: dict[str, str], body: str
) -> str:
    """
    Generate the canonical request message with ordered parameters.

    Args:
        method: The HTTP method
        path: The request path
        parameters: The query string
        signed_headers: Headers to include in signature
        body: Request body

    Returns:
        The canonical request message with ordered parameters
    """
    output = ""
    output += f"{method}\n{path}\n"
    output += f"{order_query_parameters(parameters)}\n"

    for k, v in sorted(signed_headers.items()):
        output += f"{k}:{v}\n"

    output += ";".join(sorted(signed_headers.keys())) + "\n"

    digest = hashlib.sha256(bytes(body, "latin-1")).hexdigest()
    output += digest
    return output


def generate_signature(message: bytes, key: bytes) -> str:
    """
    Generate the signature for the given message and key.

    Args:
        message: The message to use for the signature.
        key: The key to use for the signature.

    Returns:
        The signature.
    """
    inner = hmac_sha256(key, message)
    return inner.hexdigest()


def generate_auth_header(
    token: str,
    secret: str,
    method: str,
    path: str,
    params: str,
    signed_headers: dict[str, str],
    body: str,
    dt: datetime.datetime,
) -> str:
    """
    Generate the authentication header for the given token, secret, method, path, parameters, signed headers, and body.

    Args:
        token: The token to use for the authentication header.
        secret: The secret to use for the authentication header.
        method: The HTTP method to use for the authentication header.
        path: The request path to use for the authentication header.
        params: The query string to use for the authentication header.
        signed_headers: Headers to include in signature
        body: Request body
        dt: The datetime to use for the authentication header.

    Returns:
        The authentication header.
    """
    canonical = generate_canonical_request_message(
        method, path, params, signed_headers, body
    )
    key = generate_signing_key(secret, dt, "snws2_request")
    msg = generate_signing_message(dt, canonical)
    sig = generate_signature(bytes(msg, "latin-1"), key)

    output = f"SNWS2 Credential={token},SignedHeaders="

    count = 0
    for k in signed_headers:
        output += f"{k}"
        if count != len(signed_headers) - 1:
            output += ";"

        count += 1

    output += f",Signature={sig}"

    return output

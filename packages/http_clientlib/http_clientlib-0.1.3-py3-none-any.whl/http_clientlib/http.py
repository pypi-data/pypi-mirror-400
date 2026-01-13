import httpx

from http_clientlib.types import HTTPRequestMetadata, HTTPResponse

base_url = "http://localhost:8000"


def mock_http_request(http_request: HTTPRequestMetadata) -> None:
    # Log HTTP request metadata
    print(f"HTTP Request: {http_request.method} {http_request.path}")
    if http_request.path_values:
        print(f"  Path params: {http_request.path_values}")
    if http_request.query_values:
        print(f"  Query params: {http_request.query_values}")
    if http_request.body:
        print(f"  Body: {http_request.body}")


def make_http_request(http_request: HTTPRequestMetadata) -> HTTPResponse:
    """Perform an actual HTTP call based on the GeneratableHTTPRequest data."""

    response = httpx.request(
        method=http_request.method,
        url=http_request.url,
        params=http_request.query_values,
        json=http_request.body,
    )
    return response  # type: ignore[return-value]

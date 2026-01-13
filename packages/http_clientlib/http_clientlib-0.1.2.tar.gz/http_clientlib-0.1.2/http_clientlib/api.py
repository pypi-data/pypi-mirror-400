from functools import wraps
from typing import Any, Callable, ParamSpec

from http_clientlib import parsers as parser
from http_clientlib.configuration import Configuration
from http_clientlib.types import HTTPRequestMetadata, HTTPResponse

P = ParamSpec("P")

# Global default configuration
_default_configuration: Configuration | None = None


def set_default_configuration(
    base_url: str,
    http_request_function: Callable[[HTTPRequestMetadata], HTTPResponse],
) -> None:
    global _default_configuration
    _default_configuration = Configuration(
        base_url=base_url, http_request_function=http_request_function
    )


def wrap_backend_call(
    func: Callable[P, Any], configuration: Configuration | None = None
) -> Callable[P, HTTPResponse]:
    """
    Wrap a FastAPI endpoint function to simulate an HTTP call.

    Extracts:
    - Route info (HTTP method + path)
    - Path parameters
    - Query parameters
    - Request body parameters (Pydantic models)

    Serializes Pydantic models to JSON before passing to the wrapped function.
    """

    config = configuration or _default_configuration
    if config is None:
        raise RuntimeError(
            "No configuration provided and no default configuration set. "
            "Call set_default_configuration() first or pass a Configuration to wrap_endpoint()."
        )

    route_info = parser.extract_route_info(func)
    path_params = parser.extract_path_params(route_info)
    query_params, body_params = parser.extract_param_types(func, path_params)

    @wraps(func)
    def wrapper(*args, **kwargs):
        # Separate kwargs by parameter type
        path_values = {k: v for k, v in kwargs.items() if k in path_params}
        query_values = {k: v for k, v in kwargs.items() if k in query_params}
        body_values = {k: v for k, v in kwargs.items() if k in body_params}

        # Serialize body if present
        serialized_body = parser.serialize_body(body_values, body_params)

        # Parse route info into method and path
        method, path = parser.parse_route_info(route_info)

        # Create HTTP request object
        http_request = HTTPRequestMetadata(
            base_url=config.base_url,
            method=method,
            path=path,
            path_values=path_values,
            query_values=query_values,
            body=serialized_body,
        )

        return config.http_request_function(http_request)

    return wrapper

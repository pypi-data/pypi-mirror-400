from functools import wraps
from typing import Any, Callable, ParamSpec

from fastclient.configuration import Configuration
from fastclient.helpers import (
    extract_param_types,
    extract_path_params,
    extract_route_info,
    parse_route_info,
    serialize_body,
)
from fastclient.types import HTTPRequestMetadata, HTTPResponse

P = ParamSpec("P")

# Global default configuration
_default_configuration: Configuration | None = None


def set_default_configuration(configuration: Configuration) -> None:
    global _default_configuration
    _default_configuration = configuration


def http_client_decorator(
    configuration: Configuration | None = None,
) -> Callable[[Callable[P, Any]], Callable[P, Any]]:
    """
    Create a decorator that wraps FastAPI endpoint functions.

    If no configuration is provided, uses the globally set default configuration.
    """
    config = configuration if configuration is not None else _default_configuration
    if config is None:
        raise RuntimeError(
            "No configuration provided and no default configuration set. "
            "Call set_default_configuration() first or pass a Configuration to http_client_decorator()."
        )

    def decorator(func: Callable[P, Any]) -> Callable[P, Any]:
        return wrap_backend_call(func, config)

    return decorator


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

    route_info = extract_route_info(func)
    path_params = extract_path_params(route_info)
    query_params, body_params = extract_param_types(func, path_params)

    @wraps(func)
    def wrapper(*args, **kwargs):
        # Separate kwargs by parameter type
        path_values = {k: v for k, v in kwargs.items() if k in path_params}
        query_values = {k: v for k, v in kwargs.items() if k in query_params}
        body_values = {k: v for k, v in kwargs.items() if k in body_params}

        # Serialize body if present
        serialized_body = serialize_body(body_values, body_params)

        # Parse route info into method and path
        method, path = parse_route_info(route_info)

        # Create HTTP request object
        http_request = HTTPRequestMetadata(
            base_url=config.base_url,
            method=method,
            path=path,
            path_values=path_values,
            query_values=query_values,
            body=serialized_body,
        )

        return config.http_call_func(http_request)

    return wrapper

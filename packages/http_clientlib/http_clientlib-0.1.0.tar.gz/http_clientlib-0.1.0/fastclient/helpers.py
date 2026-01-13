import re
from inspect import signature
from typing import Callable, get_args, get_type_hints

from pydantic import BaseModel


def parse_route_info(route_info: str) -> tuple[str, str]:
    """Parse route info into HTTP method and path."""
    parts = route_info.split(" ", 1)
    return parts[0], parts[1] if len(parts) > 1 else "/"


def extract_route_info(func: Callable) -> str:
    """Extract the route string from function return type annotation."""
    hints = get_type_hints(func, include_extras=True)
    return get_args(hints["return"])[1]  # e.g., "GET /items/{item_id}"


def extract_path_params(route_info: str) -> set[str]:
    """Extract path parameter names from a route string."""
    return set(re.findall(r"\{(\w+)\}", route_info))


def extract_param_types(
    func: Callable, path_params: set[str]
) -> tuple[set[str], set[str]]:
    """
    Distinguish between query parameters and body parameters.

    Returns:
        (query_params, body_params): Sets of parameter names
    """
    sig = signature(func)
    all_params = set(sig.parameters.keys())

    body_params = set()
    query_params = set()

    # Identify body parameters (Pydantic BaseModel subclasses)
    for param_name, param in sig.parameters.items():
        if param_name in path_params:
            continue

        if param.annotation != param.empty:
            try:
                if isinstance(param.annotation, type) and issubclass(
                    param.annotation, BaseModel
                ):
                    body_params.add(param_name)
                    continue
            except TypeError:
                pass

        query_params.add(param_name)

    return query_params, body_params


def serialize_body(body_params: dict, body_param_names: set[str]) -> dict | None:
    """
    Serialize Pydantic model(s) to JSON-compatible dict.

    Args:
        body_params: Dictionary of parameter name -> value
        body_param_names: Set of parameter names that are body params

    Returns:
        JSON-serialized body dict or None if no body params
    """
    if not body_param_names:
        return None

    body = {}
    for param_name in body_param_names:
        if param_name in body_params:
            value = body_params[param_name]
            if isinstance(value, BaseModel):
                body[param_name] = value.model_dump(
                    exclude_unset=True, exclude_none=True
                )
            else:
                body[param_name] = value

    # If there's only one body parameter, return it unwrapped
    # (FastAPI expects the body directly, not nested under parameter name)
    if len(body) == 1:
        return next(iter(body.values()))

    return body if body else None

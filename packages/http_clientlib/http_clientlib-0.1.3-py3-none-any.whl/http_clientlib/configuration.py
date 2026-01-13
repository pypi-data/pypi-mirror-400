from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, TypeVar

from http_clientlib.http import mock_http_request

R = TypeVar("R")


@dataclass
class Configuration:
    base_url: str = "http://localhost:8000"
    http_request_function: Callable[..., Any] = mock_http_request

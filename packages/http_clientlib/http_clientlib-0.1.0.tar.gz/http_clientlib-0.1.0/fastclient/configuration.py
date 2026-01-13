from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, TypeVar

from fastclient.http import mock_http_call

R = TypeVar("R")


@dataclass
class Configuration:
    base_url: str = "http://localhost:8000"
    http_call_func: Callable[..., Any] = mock_http_call

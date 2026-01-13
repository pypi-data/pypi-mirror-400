from dataclasses import dataclass
from typing import Any, Dict, Iterable, Iterator, Optional, Protocol, runtime_checkable


@dataclass
class HTTPRequestMetadata:
    """Represents a complete HTTP request with all typed information."""

    base_url: str
    method: str  # e.g., "GET", "POST"
    path: str  # e.g., "/items/{item_id}"
    path_values: dict  # {"item_id": 123}
    query_values: dict  # {"skip": 0, "limit": 10}
    body: Optional[dict] = None  # Serialized request body

    @property
    def full_path(self) -> str:
        """Reconstruct full path with parameter substitution."""
        path = self.path
        for key, value in self.path_values.items():
            path = path.replace(f"{{{key}}}", str(value))
        return path

    def __str__(self) -> str:
        return (
            f"GeneratableHTTPRequest(method={self.method}, "
            f"path={self.full_path}, "
            f"query_values={self.query_values}, "
            f"body={self.body})"
        )

    @property
    def url(self) -> str:
        """Construct the full URL for the request."""
        return f"{self.base_url}{self.full_path}"


@runtime_checkable
class HTTPResponse(Protocol):
    """
    A library-agnostic representation of an HTTP Response.
    Works for both 'requests.Response' and 'httpx.Response'.
    """

    status_code: int
    reason_phrase: (
        str  # Note: 'requests' calls this .reason, 'httpx' calls it .reason_phrase
    )
    headers: Dict[str, str]
    encoding: str
    url: Any  # Both libraries use custom URL objects that stringify well
    is_error: bool  # httpx specific, but easy to mock/attribute-check

    @property
    def content(self) -> bytes: ...

    @property
    def text(self) -> str: ...

    def json(self, **kwargs: Any) -> Any: ...

    def raise_for_status(self) -> None: ...

    def iter_content(
        self, chunk_size: int = 1, decode_unicode: bool = False
    ) -> Iterator[Any]: ...

    def close(self) -> None: ...

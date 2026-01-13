# Overview

A client-side library that wraps server-side functions to enable RPC-style frontend API calls without hiding HTTP implementation details.

**How it works:**

- Import server functions decorated with FastAPI/Flask on the client side
- Call them as regular functions; the library translates calls into HTTP requests
- Handle the HTTP responses as per usual

A simple default HTTP implementation is included, but you can substitute your own with retry logic, caching, error handling, logging, etc.

```python
# Simple GET request without parameters
greeting_message_http = wrap_backend_call(greeting_message)
response = greeting_message_http()
print(response)

# GET request with path and query parameters
get_item_http = wrap_backend_call(get_item)
response = get_item_http(item_id=42, query="test")
print(response)

# POST request with request body
create_item_http = wrap_backend_call(post_endpoint)
response = create_item_http(data=ItemData(id=1, name="A Box"))

# Example usage: POST request using a dictionary for the request body directly
response = create_item_http(data={"id": 1, "name": "Sample Item"})
print(response)

```

## Why?

Working across HTTP boundaries introduces friction:

1. **Type information is lost** — No type inference or validation for payloads and parameters sent from client to server
2. **Developers are forced to rely on out-of-band documentation** — Type schema lives in OpenAPI/Swagger docs, not visible in your editor.

## Benefits

1. **Type safety in the editor** — Full type information available for IDE autocomplete and validation
2. **Endpoint schema visibility** — Query params, path params, request body, headers, cookies are all immediately apparent in your code
3. **Docstring availability** — Server function docstrings show up in the client IDE
4. **Code Generation not required** — Additional tooling or auto-generated code
   Changes to server signatures are immediately caught on the client side.

## Limitations

1. **Python-only** — Works for Python clients and Python backends only (FFI support for other languages possible in future)
2. **Server code must be importable** — Client needs access to server function definitions

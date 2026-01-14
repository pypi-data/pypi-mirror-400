import httpx

_client: httpx.Client | None = None


def _get_client() -> httpx.Client:
    """Return a singleton HTTP client."""
    global _client
    if _client is None:
        _client = httpx.Client(timeout=10)
    return _client


def _close_client() -> None:
    """Close the singleton client if it exists."""
    global _client
    if _client is not None:
        _client.close()
        _client = None

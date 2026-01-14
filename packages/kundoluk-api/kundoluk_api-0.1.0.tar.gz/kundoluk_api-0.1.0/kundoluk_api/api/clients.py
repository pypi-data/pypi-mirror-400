import httpx


host = "kundoluk.edu.gov.kg"
_async_client: httpx.AsyncClient= None

def get_async_client():
    global _async_client
    if _async_client is None or _async_client.is_closed:
        _async_client = httpx.AsyncClient(timeout=None)
    return _async_client

sync_client = httpx.Client(timeout=None)
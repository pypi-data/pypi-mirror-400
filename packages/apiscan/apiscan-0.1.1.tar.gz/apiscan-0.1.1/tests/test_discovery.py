import httpx
import pytest

from apiscan.discovery import discover_paths


@pytest.mark.asyncio
async def test_discover_paths_finds_openapi(monkeypatch, base_url, sample_openapi_spec):
    def handler(request: httpx.Request) -> httpx.Response:
        if str(request.url) == base_url + "/openapi.json":
            return httpx.Response(200, json=sample_openapi_spec)
        return httpx.Response(404)

    transport = httpx.MockTransport(handler)

    # Monkeypatch httpx.AsyncClient used inside discover_paths
    real_async_client = httpx.AsyncClient

    def client_factory(*args, **kwargs):
        kwargs["transport"] = transport
        kwargs["follow_redirects"] = True
        return real_async_client(*args, **kwargs)

    monkeypatch.setattr(httpx, "AsyncClient", client_factory)

    result = await discover_paths(base_url, timeout=5)
    assert result.found is True
    assert result.spec_url.endswith("/openapi.json")
    assert "/users" in result.paths
    assert "/health" in result.paths


@pytest.mark.asyncio
async def test_discover_paths_not_found(monkeypatch, base_url):
    transport = httpx.MockTransport(lambda request: httpx.Response(404))

    real_async_client = httpx.AsyncClient

    def client_factory(*args, **kwargs):
        kwargs["transport"] = transport
        kwargs["follow_redirects"] = True
        return real_async_client(*args, **kwargs)

    monkeypatch.setattr(httpx, "AsyncClient", client_factory)

    result = await discover_paths(base_url, timeout=5)
    assert result.found is False
    assert result.paths == []

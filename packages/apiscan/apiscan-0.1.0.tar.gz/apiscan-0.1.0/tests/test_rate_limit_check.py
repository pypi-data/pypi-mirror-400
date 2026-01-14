import httpx
import pytest

from apiscan.checks.rate_limit import run
from apiscan.http import HttpClient


@pytest.mark.asyncio
async def test_rate_limit_detected(monkeypatch):
    count = {"n": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        count["n"] += 1
        if count["n"] >= 5:
            return httpx.Response(429, headers={"Retry-After": "5"})
        return httpx.Response(200, json={"ok": True})

    transport = httpx.MockTransport(handler)

    # Patch AsyncClient creation inside HttpClient to use our transport
    real_async_client = httpx.AsyncClient

    def client_factory(*args, **kwargs):
        kwargs["transport"] = transport
        kwargs["follow_redirects"] = True
        return real_async_client(*args, **kwargs)

    monkeypatch.setattr(httpx, "AsyncClient", client_factory)

    async with HttpClient("https://example.com") as client:
        findings = await run(client, path="/", burst=10, delay=0.0)

    assert findings
    assert findings[0].name in ("Rate limiting detected", "Rate limit headers present")

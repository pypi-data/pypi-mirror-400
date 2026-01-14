import httpx
import pytest

from apiscan.checks.rate_limit import run as rate_run
from apiscan.checks.info_leak import run as leak_run
from apiscan.http import HttpClient


def test_info_leak_header_fingerprinting_low():
    r = httpx.Response(200, headers={"Server": "nginx", "X-Powered-By": "Express"})
    findings = leak_run(r)
    assert any(f.severity.value == "low" for f in findings)


@pytest.mark.asyncio
async def test_rate_limit_headers_present(monkeypatch):
    # Always 200 but with X-RateLimit headers
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={"ok": True},
            headers={"X-RateLimit-Limit": "60", "X-RateLimit-Remaining": "59"},
        )

    transport = httpx.MockTransport(handler)

    real_async_client = httpx.AsyncClient

    def client_factory(*args, **kwargs):
        kwargs["transport"] = transport
        kwargs["follow_redirects"] = True
        return real_async_client(*args, **kwargs)

    monkeypatch.setattr(httpx, "AsyncClient", client_factory)

    async with HttpClient("https://example.com") as client:
        findings = await rate_run(client, path="/", burst=5, delay=0.0)

    assert findings
    assert findings[0].name == "Rate limit headers present"

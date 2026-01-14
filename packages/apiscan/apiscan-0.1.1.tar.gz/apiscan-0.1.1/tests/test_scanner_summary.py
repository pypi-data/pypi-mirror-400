import httpx
import pytest

from apiscan.http import HttpClient
from apiscan.scanner import Scanner


@pytest.mark.asyncio
async def test_scanner_produces_summary(monkeypatch):
    def handler(request: httpx.Request) -> httpx.Response:
        url = str(request.url)
        # GET /
        if request.method == "GET" and url.endswith("/"):
            return httpx.Response(
                200,
                text="ok",
                headers={"Server": "demo"}  # missing security headers => medium finding
            )
        # GET /health
        if request.method == "GET" and url.endswith("/health"):
            return httpx.Response(500, text="Traceback (most recent call last): ...")
        # OPTIONS /
        if request.method == "OPTIONS" and url.endswith("/"):
            return httpx.Response(
                204,
                headers={
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Credentials": "true",
                },
            )
        return httpx.Response(404)

    transport = httpx.MockTransport(handler)

    # Patch httpx.AsyncClient used by HttpClient and by scanner's redirect probe
    real_async_client = httpx.AsyncClient

    def client_factory(*args, **kwargs):
        kwargs["transport"] = transport
        kwargs["follow_redirects"] = True
        return real_async_client(*args, **kwargs)

    monkeypatch.setattr(httpx, "AsyncClient", client_factory)

    async with HttpClient("https://example.com") as client:
        scanner = Scanner(client, concurrency=5)
        result = await scanner.scan(paths=["/", "/health"])

    assert result.summary is not None
    # We expect some findings
    assert result.summary.medium >= 1  # missing headers
    assert result.summary.high >= 1    # stack trace or CORS misconfig
    assert result.summary.risk_score > 0

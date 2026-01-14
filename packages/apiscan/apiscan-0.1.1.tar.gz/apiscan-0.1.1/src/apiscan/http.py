import httpx


class HttpClient:
    def __init__(self, base_url: str, timeout: int = 10):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.client: httpx.AsyncClient | None = None

    async def __aenter__(self):
        self.client = httpx.AsyncClient(timeout=self.timeout, follow_redirects=True)
        return self

    async def __aexit__(self, exc_type, exc, tb):
        if self.client:
            await self.client.aclose()

    async def get(self, path: str = "/"):
        assert self.client is not None, "HttpClient must be used with 'async with'"
        return await self.client.get(self.base_url + path)

    async def options(self, path: str = "/"):
        assert self.client is not None, "HttpClient must be used with 'async with'"
        return await self.client.options(self.base_url + path)

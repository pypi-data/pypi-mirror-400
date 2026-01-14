from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

import httpx


COMMON_SPEC_PATHS = [
    "/openapi.json",
    "/swagger.json",
    "/api-docs",
    "/api-docs/swagger.json",
    "/v3/api-docs",
    "/v3/api-docs/swagger-config",
]


@dataclass
class DiscoveryResult:
    found: bool
    spec_url: str | None
    paths: list[str]
    note: str | None = None


def _extract_openapi_paths(spec: dict[str, Any]) -> list[str]:
    """
    Supports OpenAPI/Swagger specs where paths live under the 'paths' object.
    """
    paths_obj = spec.get("paths")
    if not isinstance(paths_obj, dict):
        return []
    # return keys like "/users", "/health"
    paths = [p for p in paths_obj.keys() if isinstance(p, str) and p.startswith("/")]
    return sorted(set(paths))


async def discover_paths(base_url: str, timeout: int = 10) -> DiscoveryResult:
    """
    Attempts to discover API paths from common OpenAPI/Swagger endpoints.
    Safe: only GETs docs endpoints.
    """
    async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
        for spec_path in COMMON_SPEC_PATHS:
            url = base_url.rstrip("/") + spec_path
            try:
                r = await client.get(url, headers={"Accept": "application/json"})
                if r.status_code >= 400:
                    continue

                # some endpoints return yaml or html; try json first
                try:
                    spec = r.json()
                except Exception:
                    continue

                if not isinstance(spec, dict):
                    continue

                paths = _extract_openapi_paths(spec)
                if paths:
                    return DiscoveryResult(found=True, spec_url=url, paths=paths)

                # Sometimes swagger-config returns a pointer; keep it simple for v0.2
                # If no paths, continue to try next candidate.
            except Exception:
                continue

    return DiscoveryResult(found=False, spec_url=None, paths=[], note="No OpenAPI/Swagger spec detected at common endpoints.")

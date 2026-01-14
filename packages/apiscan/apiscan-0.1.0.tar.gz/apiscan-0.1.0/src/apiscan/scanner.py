import asyncio
from urllib.parse import urlparse

import httpx

from apiscan.checks import (
    headers_run,
    tls_run,
    cors_run,
    rate_limit_run,
    info_leak_run,
)
from apiscan.models import ScanResult, PathResult, Finding, Severity, SeveritySummary


class Scanner:
    def __init__(self, client, concurrency: int = 10):
        self.client = client
        self.concurrency = concurrency

    async def _probe_http_redirect(self) -> dict | None:
        parsed = urlparse(self.client.base_url)
        if not parsed.hostname:
            return None

        http_url = f"http://{parsed.hostname}"
        if parsed.port:
            http_url = f"http://{parsed.hostname}:{parsed.port}"

        try:
            async with httpx.AsyncClient(timeout=10, follow_redirects=True) as c:
                r = await c.get(http_url + "/")

            final = str(r.url)
            if final.startswith("https://"):
                return {"mode": "redirect_to_https", "http_url": http_url + "/", "final_url": final, "status_code": r.status_code}
            if final.startswith("http://"):
                return {"mode": "http_ok", "http_url": http_url + "/", "final_url": final, "status_code": r.status_code}
            return {"mode": "unknown", "http_url": http_url + "/", "final_url": final, "status_code": r.status_code}
        except Exception as e:
            return {"mode": "error", "error": str(e), "http_url": http_url + "/"}

    def _compute_summary(self, global_findings: list[Finding], path_results: list[PathResult]) -> SeveritySummary:
        summary = SeveritySummary()

        all_findings = list(global_findings)
        for pr in path_results:
            all_findings.extend(pr.findings)

        for f in all_findings:
            if f.severity == Severity.info:
                summary.info += 1
            elif f.severity == Severity.low:
                summary.low += 1
            elif f.severity == Severity.medium:
                summary.medium += 1
            elif f.severity == Severity.high:
                summary.high += 1

        # Simple weighted score (tweak later)
        summary.risk_score = (summary.high * 5) + (summary.medium * 3) + (summary.low * 1)
        return summary

    async def _scan_path(self, sem: asyncio.Semaphore, path: str) -> PathResult:
        if not path.startswith("/"):
            path = "/" + path

        async with sem:
            findings = []
            status_code = None

            try:
                resp = await self.client.get(path)
                status_code = resp.status_code

                findings.extend(headers_run(resp))
                findings.extend(info_leak_run(resp))

            except Exception as e:
                findings.append(
                    Finding(
                        name="Request error",
                        severity=Severity.medium,
                        description="Failed to fetch the endpoint.",
                        evidence={"path": path, "error": str(e)},
                    )
                )

            return PathResult(path=path, status_code=status_code, findings=findings)

    async def scan(self, paths: list[str] | None = None) -> ScanResult:
        if not paths:
            paths = ["/"]

        global_findings: list[Finding] = []

        # Global TLS check
        http_probe = await self._probe_http_redirect()
        global_findings.extend(tls_run(self.client.base_url, http_probe))

        # Global CORS check
        try:
            options_response = await self.client.options("/")
            global_findings.extend(cors_run(options_response))
        except Exception:
            pass

        # Global rate limiting check (async)
        global_findings.extend(await rate_limit_run(self.client, path="/", burst=20, delay=0.0))

        # Concurrent per-path scan
        sem = asyncio.Semaphore(self.concurrency)
        tasks = [self._scan_path(sem, p) for p in paths]
        path_results = await asyncio.gather(*tasks)

        summary = self._compute_summary(global_findings, path_results)

        return ScanResult(
            target=self.client.base_url,
            paths_scanned=paths,
            path_results=path_results,
            global_findings=global_findings,
            summary=summary,
        )

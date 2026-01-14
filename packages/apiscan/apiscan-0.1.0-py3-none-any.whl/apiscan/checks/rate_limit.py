import time
from apiscan.models import Finding, Severity

RATE_HEADERS = [
    "retry-after",
    "x-ratelimit-limit",
    "x-ratelimit-remaining",
    "x-ratelimit-reset",
    "ratelimit-limit",
    "ratelimit-remaining",
    "ratelimit-reset",
]

async def run(client, path: str = "/", burst: int = 20, delay: float = 0.0):
    findings = []

    statuses = []
    seen_headers = {}
    throttled = False
    timings = []

    for _ in range(burst):
        start = time.perf_counter()
        try:
            r = await client.get(path)
            elapsed = time.perf_counter() - start
            timings.append(elapsed)

            statuses.append(r.status_code)

            hdrs = {k.lower(): v for k, v in r.headers.items()}
            for h in RATE_HEADERS:
                if h in hdrs:
                    seen_headers[h] = hdrs[h]

            if r.status_code == 429:
                throttled = True

            body = ""
            try:
                body = (r.text or "")[:500].lower()
            except Exception:
                body = ""

            if "rate limit" in body or "too many requests" in body:
                throttled = True

        except Exception as e:
            statuses.append("error")
            seen_headers["error"] = str(e)
            break

        if delay:
            time.sleep(delay)

    if throttled:
        findings.append(
            Finding(
                name="Rate limiting detected",
                severity=Severity.info,
                description="The API appears to throttle requests (good).",
                evidence={"burst": burst, "path": path, "statuses": statuses[-10:], "rate_headers": seen_headers},
            )
        )
        return findings

    if seen_headers:
        findings.append(
            Finding(
                name="Rate limit headers present",
                severity=Severity.info,
                description="Rate limiting headers were observed. Throttling may be enforced.",
                evidence={"burst": burst, "path": path, "statuses": statuses[-10:], "rate_headers": seen_headers},
            )
        )
        return findings

    findings.append(
        Finding(
            name="Rate limiting not detected",
            severity=Severity.medium,
            description="No rate limiting signals were observed in a small request burst. This may increase abuse risk.",
            evidence={"burst": burst, "path": path, "statuses": statuses[-10:], "note": "Heuristic check."},
        )
    )
    return findings

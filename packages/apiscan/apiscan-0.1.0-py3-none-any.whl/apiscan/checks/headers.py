from apiscan.models import Finding, Severity

SECURITY_HEADERS = [
    "X-Content-Type-Options",
    "X-Frame-Options",
    "Content-Security-Policy",
    "Referrer-Policy",
    "Strict-Transport-Security",
]

def run(response):
    missing = []
    for header in SECURITY_HEADERS:
        if header not in response.headers:
            missing.append(header)

    findings = []

    if missing:
        findings.append(
            Finding(
                name="Missing security headers",
                severity=Severity.medium,
                description="The API response is missing important security headers.",
                evidence={"missing": missing},
            )
        )

    return findings

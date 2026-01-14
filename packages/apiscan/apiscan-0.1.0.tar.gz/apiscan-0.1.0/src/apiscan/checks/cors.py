from apiscan.models import Finding, Severity


def run(options_response):
    """
    CORS check (safe):
    - Looks at CORS headers from OPTIONS response.
    - Flags wildcard ACAO with credentials enabled.
    """
    findings = []

    headers = {k.lower(): v for k, v in options_response.headers.items()}

    acao = headers.get("access-control-allow-origin")
    acac = headers.get("access-control-allow-credentials")
    acam = headers.get("access-control-allow-methods")
    acah = headers.get("access-control-allow-headers")

    # If no CORS headers, that's not necessarily a vulnerability.
    if not acao and not acac and not acam and not acah:
        findings.append(
            Finding(
                name="CORS headers not detected",
                severity=Severity.info,
                description="No CORS headers were observed in the OPTIONS response.",
                evidence={"status_code": options_response.status_code},
            )
        )
        return findings

    # Dangerous pattern: wildcard origin + credentials
    if acao == "*" and (acac or "").lower() == "true":
        findings.append(
            Finding(
                name="Potentially unsafe CORS configuration",
                severity=Severity.high,
                description="Access-Control-Allow-Origin is '*' while credentials are allowed.",
                evidence={
                    "access-control-allow-origin": acao,
                    "access-control-allow-credentials": acac,
                    "access-control-allow-methods": acam,
                    "access-control-allow-headers": acah,
                },
            )
        )
        return findings

    # Broad but common configuration: reflect origin or specific origin
    findings.append(
        Finding(
            name="CORS configuration detected",
            severity=Severity.info,
            description="CORS headers were detected. Review allowed origins and credentials if sensitive endpoints exist.",
            evidence={
                "access-control-allow-origin": acao,
                "access-control-allow-credentials": acac,
                "access-control-allow-methods": acam,
                "access-control-allow-headers": acah,
            },
        )
    )

    return findings

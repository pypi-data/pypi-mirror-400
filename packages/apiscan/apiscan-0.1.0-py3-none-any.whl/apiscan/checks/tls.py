from apiscan.models import Finding, Severity


def run(base_url: str, http_probe_result: dict | None = None):
    """
    TLS check (safe, non-invasive):
    - Warn if base URL is not https.
    - If we probed http:// and got redirected to https://, note it (good).
    - If http:// works without redirect, flag it (risk).
    """
    findings = []

    if base_url.startswith("https://"):
        # Good: HTTPS URL given. Still useful to report if HTTP also works.
        if http_probe_result:
            mode = http_probe_result.get("mode")
            if mode == "redirect_to_https":
                findings.append(
                    Finding(
                        name="HTTP redirects to HTTPS",
                        severity=Severity.info,
                        description="HTTP requests are redirected to HTTPS (good).",
                        evidence=http_probe_result,
                    )
                )
            elif mode == "http_ok":
                findings.append(
                    Finding(
                        name="HTTP endpoint accessible",
                        severity=Severity.medium,
                        description="The service is accessible over HTTP without redirecting to HTTPS.",
                        evidence=http_probe_result,
                    )
                )
        return findings

    # If user supplied http://, warn immediately
    if base_url.startswith("http://"):
        findings.append(
            Finding(
                name="Target is not using HTTPS",
                severity=Severity.high,
                description="Target base URL uses HTTP. Sensitive data may be exposed in transit.",
                evidence={"base_url": base_url},
            )
        )

        # If probe indicates redirect, downgrade severity
        if http_probe_result and http_probe_result.get("mode") == "redirect_to_https":
            findings[-1] = Finding(
                name="Target redirects HTTP to HTTPS",
                severity=Severity.medium,
                description="Base URL uses HTTP, but it redirects to HTTPS. Prefer scanning the HTTPS URL.",
                evidence=http_probe_result,
            )

    return findings

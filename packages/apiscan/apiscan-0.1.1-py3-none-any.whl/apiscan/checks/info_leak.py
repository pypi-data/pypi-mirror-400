import re
from apiscan.models import Finding, Severity

STACKTRACE_PATTERNS = [
    r"traceback \(most recent call last\)",
    r"exception in thread",
    r"stack trace",
    r"at\s+\w+\..+\(.+:\d+\)",       # Java-style "at pkg.Class(file:line)"
    r"syntaxerror:",
    r"nameerror:",
    r"nullpointerexception",
    r"sqlstate",
    r"fatal error",
]

LEAKY_HEADERS = [
    "server",
    "x-powered-by",
    "x-aspnet-version",
    "x-runtime",
]

def run(response):
    findings = []

    # Header leakage
    hdrs = {k.lower(): v for k, v in response.headers.items()}
    leaked = {h: hdrs[h] for h in LEAKY_HEADERS if h in hdrs and hdrs[h]}

    if leaked:
        findings.append(
            Finding(
                name="Potential information leakage via headers",
                severity=Severity.low,
                description="The response includes technology-identifying headers that may aid attackers in fingerprinting.",
                evidence=leaked,
            )
        )

    # Body leakage (best-effort)
    body = ""
    try:
        body = (response.text or "")[:1500]
    except Exception:
        body = ""

    body_l = body.lower()

    matched = []
    for pat in STACKTRACE_PATTERNS:
        if re.search(pat, body_l, re.IGNORECASE):
            matched.append(pat)

    # Common framework hints
    framework_hints = []
    if "django" in body_l and "debug" in body_l:
        framework_hints.append("django debug content")
    if "werkzeug" in body_l or "flask" in body_l:
        framework_hints.append("flask/werkzeug debug content")
    if "rails" in body_l and "actioncontroller" in body_l:
        framework_hints.append("rails error content")

    if matched or framework_hints:
        findings.append(
            Finding(
                name="Potential verbose error / stack trace exposure",
                severity=Severity.high,
                description="The response body appears to contain stack trace or debug information.",
                evidence={
                    "matched_patterns": matched,
                    "framework_hints": framework_hints,
                    "snippet": body[:500],
                },
            )
        )

    return findings

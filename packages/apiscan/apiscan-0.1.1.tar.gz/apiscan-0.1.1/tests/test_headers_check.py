import httpx
from apiscan.checks.headers import run


def test_headers_check_flags_missing_headers():
    r = httpx.Response(200, headers={"Server": "demo"})
    findings = run(r)

    assert findings, "Should flag missing security headers"
    assert findings[0].name == "Missing security headers"
    assert "missing" in findings[0].evidence

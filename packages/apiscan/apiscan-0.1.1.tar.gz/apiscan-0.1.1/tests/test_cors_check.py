import httpx
from apiscan.checks.cors import run


def test_cors_flags_wildcard_with_credentials():
    r = httpx.Response(
        204,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Credentials": "true",
            "Access-Control-Allow-Methods": "GET,POST",
        },
    )
    findings = run(r)
    assert findings
    assert findings[0].severity.value == "high"


def test_cors_no_headers_is_info():
    r = httpx.Response(204, headers={})
    findings = run(r)
    assert findings
    assert findings[0].severity.value == "info"

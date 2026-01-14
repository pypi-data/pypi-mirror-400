from apiscan.checks.tls import run
from apiscan.models import Severity


def test_tls_https_with_http_redirect_is_info():
    findings = run(
        "https://example.com",
        {"mode": "redirect_to_https", "http_url": "http://example.com/", "final_url": "https://example.com/", "status_code": 200},
    )
    assert findings
    assert findings[0].severity == Severity.info


def test_tls_https_with_http_ok_is_medium():
    findings = run(
        "https://example.com",
        {"mode": "http_ok", "http_url": "http://example.com/", "final_url": "http://example.com/", "status_code": 200},
    )
    assert findings
    assert findings[0].severity == Severity.medium


def test_tls_http_base_url_is_high_or_medium():
    # If user supplies HTTP, we should warn
    findings = run("http://example.com", None)
    assert findings
    assert findings[0].severity in (Severity.high, Severity.medium)

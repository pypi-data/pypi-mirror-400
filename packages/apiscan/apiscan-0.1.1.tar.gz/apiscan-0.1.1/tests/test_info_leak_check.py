import httpx
from apiscan.checks.info_leak import run


def test_info_leak_detects_stacktrace():
    body = "Traceback (most recent call last):\\n  File ..."
    r = httpx.Response(500, text=body, headers={"Server": "gunicorn"})
    findings = run(r)

    # should include high severity stack trace finding
    assert any(f.severity.value == "high" for f in findings)

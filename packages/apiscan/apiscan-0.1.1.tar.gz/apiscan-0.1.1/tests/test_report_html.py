from pathlib import Path

from apiscan.models import ScanResult, PathResult, Finding, Severity, SeveritySummary
from apiscan.report import generate_html_report


def test_generate_html_report_writes_file(tmp_path: Path):
    result = ScanResult(
        target="https://example.com",
        paths_scanned=["/"],
        path_results=[
            PathResult(
                path="/",
                status_code=200,
                findings=[
                    Finding(
                        name="Missing security headers",
                        severity=Severity.medium,
                        description="Missing headers.",
                        evidence={"missing": ["X-Frame-Options"]},
                    )
                ],
            )
        ],
        global_findings=[
            Finding(
                name="CORS configuration detected",
                severity=Severity.info,
                description="CORS headers observed.",
                evidence={"access-control-allow-origin": "*"},
            )
        ],
        summary=SeveritySummary(info=1, medium=1, risk_score=3),
    )

    out = tmp_path / "report.html"
    generate_html_report(result, str(out))

    assert out.exists()
    html = out.read_text(encoding="utf-8")
    assert "APIScan Report" in html
    assert "https://example.com" in html
    assert "Missing security headers" in html

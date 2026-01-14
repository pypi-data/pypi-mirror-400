from pathlib import Path
import json
import pytest

import apiscan.cli as cli
from apiscan.models import ScanResult, PathResult, Finding, Severity, SeveritySummary


def _fake_result():
    return ScanResult(
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
        global_findings=[],
        summary=SeveritySummary(medium=1, risk_score=3),
    )


@pytest.mark.asyncio
async def test_cli_output_dir_creates_default_reports(tmp_path: Path, monkeypatch):
    class DummyClient:
        base_url = "https://example.com"

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

    class DummyScanner:
        def __init__(self, client, concurrency=10):
            pass

        async def scan(self, paths=None):
            return _fake_result()

    monkeypatch.setattr(cli, "HttpClient", lambda url, timeout=10: DummyClient())
    monkeypatch.setattr(cli, "Scanner", DummyScanner)

    def fake_generate_html_report(result, output_html):
        Path(output_html).write_text("<html>APIScan Report</html>", encoding="utf-8")

    monkeypatch.setattr(cli, "generate_html_report", fake_generate_html_report)

    outdir = tmp_path / "reports"

    await cli.run_scan(
        url="https://example.com",
        user_paths=["/"],
        discover=False,
        max_paths=10,
        json_output=None,
        html_output=None,
        output_dir=str(outdir),
        concurrency=5,
        timeout=5,
    )

    json_path = outdir / "apiscan_report.json"
    html_path = outdir / "apiscan_report.html"

    assert json_path.exists()
    assert html_path.exists()

    data = json.loads(json_path.read_text(encoding="utf-8"))
    assert data["target"] == "https://example.com"
    assert "summary" in data
    assert "path_results" in data


@pytest.mark.asyncio
async def test_cli_output_dir_respects_custom_filenames(tmp_path: Path, monkeypatch):
    class DummyClient:
        base_url = "https://example.com"

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

    class DummyScanner:
        def __init__(self, client, concurrency=10):
            pass

        async def scan(self, paths=None):
            return _fake_result()

    monkeypatch.setattr(cli, "HttpClient", lambda url, timeout=10: DummyClient())
    monkeypatch.setattr(cli, "Scanner", DummyScanner)

    def fake_generate_html_report(result, output_html):
        Path(output_html).write_text("<html>APIScan Report</html>", encoding="utf-8")

    monkeypatch.setattr(cli, "generate_html_report", fake_generate_html_report)

    outdir = tmp_path / "reports"

    await cli.run_scan(
        url="https://example.com",
        user_paths=["/"],
        discover=False,
        max_paths=10,
        json_output="custom.json",
        html_output="custom.html",
        output_dir=str(outdir),
        concurrency=5,
        timeout=5,
    )

    assert (outdir / "custom.json").exists()
    assert (outdir / "custom.html").exists()

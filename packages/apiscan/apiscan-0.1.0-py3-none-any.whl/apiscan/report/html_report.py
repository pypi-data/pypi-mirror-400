from __future__ import annotations

from jinja2 import Environment, FileSystemLoader, select_autoescape
from pathlib import Path
from importlib import resources

from apiscan.models import ScanResult


def _get_templates_path() -> Path:
    # Works in editable installs and packaged installs
    return Path(resources.files("apiscan") / "templates")


def generate_html_report(result: ScanResult, output_html: str) -> None:
    templates_dir = _get_templates_path()

    env = Environment(
        loader=FileSystemLoader(str(templates_dir)),
        autoescape=select_autoescape(["html", "xml"]),
    )

    template = env.get_template("report.html.j2")

    html = template.render(
        target=result.target,
        summary=result.summary.model_dump(),
        global_findings=[f.model_dump() for f in result.global_findings],
        path_results=[
            {
                "path": pr.path,
                "status_code": pr.status_code,
                "findings": [f.model_dump() for f in pr.findings],
            }
            for pr in result.path_results
        ],
        paths_scanned=result.paths_scanned,
    )

    with open(output_html, "w", encoding="utf-8") as f:
        f.write(html)

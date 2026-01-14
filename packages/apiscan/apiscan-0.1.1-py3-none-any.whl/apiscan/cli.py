import argparse
import asyncio
from pathlib import Path

from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from apiscan.http import HttpClient
from apiscan.scanner import Scanner
from apiscan.report import generate_html_report
from apiscan.discovery import discover_paths

console = Console()


def render_summary(summary):
    return (
        f"high: {summary.high}  "
        f"medium: {summary.medium}  "
        f"low: {summary.low}  "
        f"info: {summary.info}\n"
        f"risk_score: {summary.risk_score}"
    )


def _resolve_output_path(output_dir: str | None, filename: str | None, default_name: str) -> str | None:
    if not output_dir:
        return filename

    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    if filename is None:
        return str(out_dir / default_name)

    p = Path(filename)
    if p.is_absolute():
        return str(p)

    return str(out_dir / p)


def _merge_paths(user_paths: list[str], discovered_paths: list[str], max_paths: int) -> list[str]:
    cleaned = []

    def add(p: str):
        if not p:
            return
        if not p.startswith("/"):
            p = "/" + p
        cleaned.append(p)

    for p in user_paths:
        add(p)
    for p in discovered_paths:
        add(p)

    # Dedupe while preserving order
    seen = set()
    merged = []
    for p in cleaned:
        if p not in seen:
            seen.add(p)
            merged.append(p)

    return merged[:max_paths]


async def run_scan(
    url: str,
    user_paths: list[str],
    discover: bool,
    max_paths: int,
    json_output: str | None,
    html_output: str | None,
    output_dir: str | None,
    concurrency: int,
    timeout: int,
):
    json_path = _resolve_output_path(output_dir, json_output, "apiscan_report.json")
    html_path = _resolve_output_path(output_dir, html_output, "apiscan_report.html")

    discovered = []
    spec_url = None

    if discover:
        console.print("[bold]Discovering endpoints via OpenAPI/Swagger...[/bold]")
        d = await discover_paths(url, timeout=timeout)
        if d.found:
            discovered = d.paths
            spec_url = d.spec_url
            console.print(f"[green]Found OpenAPI spec:[/green] {spec_url}")
            console.print(f"[green]Discovered {len(discovered)} paths[/green]\n")
        else:
            console.print("[yellow]No OpenAPI spec found at common endpoints.[/yellow]\n")

    paths = _merge_paths(user_paths, discovered, max_paths=max_paths)

    console.print(f"[bold]Scanning {url}[/bold]")
    console.print(f"Paths to scan ({len(paths)}): {', '.join(paths[:10])}" + (" ..." if len(paths) > 10 else "") + "\n")

    async with HttpClient(url, timeout=timeout) as client:
        scanner = Scanner(client, concurrency=concurrency)
        result = await scanner.scan(paths=paths)

    # attach discovery info into JSON/HTML via evidence in a global finding (simple and visible)
    if discover and spec_url:
        # Don’t import Finding/Severity here to keep CLI simple; scanner output is already good.
        pass

    console.print(Panel.fit(render_summary(result.summary), title="Severity Summary"))

    if result.global_findings:
        table = Table(title="Global Findings (Target-wide)")
        table.add_column("Severity")
        table.add_column("Issue")
        table.add_column("Description")
        for f in result.global_findings:
            table.add_row(f.severity, f.name, f.description)
        console.print(table)
        console.print()

    for pr in result.path_results:
        if not pr.findings:
            console.print(f"[green]{pr.path} ({pr.status_code}) - No issues found[/green]")
            continue

        table = Table(title=f"Findings for {pr.path} (status {pr.status_code})")
        table.add_column("Severity")
        table.add_column("Issue")
        table.add_column("Description")
        for f in pr.findings:
            table.add_row(f.severity, f.name, f.description)
        console.print(table)
        console.print()

    if json_path:
        Path(json_path).parent.mkdir(parents=True, exist_ok=True)
        with open(json_path, "w", encoding="utf-8") as f:
            f.write(result.model_dump_json(indent=2))
        console.print(f"[yellow]JSON report saved to {json_path}[/yellow]")

    if html_path:
        Path(html_path).parent.mkdir(parents=True, exist_ok=True)
        generate_html_report(result, html_path)
        console.print(f"[yellow]HTML report saved to {html_path}[/yellow]")


def main():
    parser = argparse.ArgumentParser(description="APIScan – Public API Security Scanner (safe checks)")

    parser.add_argument("url", help="Target API base URL (example: https://api.example.com)")

    parser.add_argument(
        "--paths",
        nargs="*",
        default=["/"],
        help="Paths to scan (example: --paths / /health /login). Used in addition to discovered paths if --discover is enabled.",
    )

    parser.add_argument(
        "--discover",
        action="store_true",
        help="Attempt to discover endpoints from OpenAPI/Swagger (openapi.json, swagger.json, v3/api-docs, etc).",
    )

    parser.add_argument(
        "--max-paths",
        type=int,
        default=30,
        help="Max number of paths to scan after merging user and discovered paths (default: 30).",
    )

    parser.add_argument("--json", dest="json_output", help="Write scan report to JSON file (default inside output-dir)")
    parser.add_argument("--report-html", dest="html_output", help="Write scan report to HTML file (default inside output-dir)")
    parser.add_argument("--output-dir", dest="output_dir", help="Directory to store outputs (creates default JSON/HTML names)")

    parser.add_argument("--concurrency", type=int, default=10, help="Concurrent requests for path scanning")
    parser.add_argument("--timeout", type=int, default=10, help="Request timeout in seconds")

    args = parser.parse_args()

    asyncio.run(
        run_scan(
            url=args.url,
            user_paths=args.paths,
            discover=args.discover,
            max_paths=args.max_paths,
            json_output=args.json_output,
            html_output=args.html_output,
            output_dir=args.output_dir,
            concurrency=args.concurrency,
            timeout=args.timeout,
        )
    )


if __name__ == "__main__":
    main()

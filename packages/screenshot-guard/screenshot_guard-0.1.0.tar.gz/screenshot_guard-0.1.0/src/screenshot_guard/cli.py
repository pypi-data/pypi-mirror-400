"""Command-line interface for Screenshot Guard."""

import sys
import logging
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from screenshot_guard import __version__
from screenshot_guard.scanner import Scanner
from screenshot_guard.detector import SecretDetector, Finding
from screenshot_guard.ocr import OCREngine
from screenshot_guard.reporters import JSONReporter, SARIFReporter, MarkdownReporter

console = Console()
logger = logging.getLogger("screenshot_guard")


def setup_logging(verbose: bool) -> None:
    """Configure logging."""
    level = logging.DEBUG if verbose else logging.WARNING
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )


@click.group()
@click.version_option(version=__version__)
@click.option("-v", "--verbose", is_flag=True, help="Enable verbose output")
def cli(verbose: bool) -> None:
    """Screenshot Guard - Secret Scanner with OCR Superpowers.

    Finds secrets in code AND screenshots.
    """
    setup_logging(verbose)


@cli.command()
@click.argument("path", type=click.Path(exists=True))
@click.option(
    "-f", "--format",
    type=click.Choice(["table", "json", "sarif", "markdown"]),
    default="table",
    help="Output format",
)
@click.option("-o", "--output", type=click.Path(), help="Output file path")
@click.option(
    "-s", "--severity",
    type=click.Choice(["critical", "high", "medium", "low", "all"]),
    default="all",
    help="Minimum severity to report",
)
@click.option("--ocr/--no-ocr", default=True, help="Enable/disable OCR for images")
@click.option(
    "--backend",
    type=click.Choice(["llamacpp", "ollama", "cloud"]),
    default="llamacpp",
    help="OCR backend to use",
)
@click.option("--fail-on-findings", is_flag=True, help="Exit with code 1 if secrets found")
def scan(
    path: str,
    format: str,
    output: Optional[str],
    severity: str,
    ocr: bool,
    backend: str,
    fail_on_findings: bool,
) -> None:
    """Scan directory or file for exposed secrets.

    PATH can be a file or directory to scan.
    """
    path_obj = Path(path).resolve()

    # Header
    console.print(Panel.fit(
        "[bold blue]Screenshot Guard[/bold blue]\n"
        f"Scanning: {path_obj}",
        border_style="blue",
    ))

    # Initialize components
    min_severity = "low" if severity == "all" else severity
    detector = SecretDetector(min_severity=min_severity)

    ocr_engine = None
    if ocr:
        try:
            ocr_engine = OCREngine(backend=backend)
            console.print(f"[dim]OCR enabled ({backend} backend)[/dim]")
        except ImportError:
            console.print("[yellow]OCR not available - install with: pip install screenshot-guard[ocr][/yellow]")

    scanner = Scanner(detector=detector, ocr_engine=ocr_engine)

    # Run scan
    console.print("[dim]Scanning...[/dim]")
    findings = scanner.scan(path_obj)
    console.print("[dim]Scan complete.[/dim]")

    # Filter by severity if needed
    if severity != "all":
        severity_order = {"critical": 4, "high": 3, "medium": 2, "low": 1}
        min_level = severity_order.get(severity, 0)
        findings = [f for f in findings if severity_order.get(f.severity, 0) >= min_level]

    # Report results
    if findings:
        console.print(f"\n[bold red]Found {len(findings)} potential secrets![/bold red]\n")
        _output_findings(findings, format, output)

        if fail_on_findings:
            sys.exit(1)
    else:
        console.print("\n[bold green]No secrets found.[/bold green]")


def _output_findings(findings: list[Finding], format: str, output: Optional[str]) -> None:
    """Output findings in the specified format."""
    if format == "table":
        _print_findings_table(findings)
    elif format == "json":
        reporter = JSONReporter()
        result = reporter.generate(findings)
        if output:
            Path(output).write_text(result)
            console.print(f"[dim]Report saved to {output}[/dim]")
        else:
            console.print(result)
    elif format == "sarif":
        reporter = SARIFReporter()
        result = reporter.generate(findings)
        if output:
            Path(output).write_text(result)
            console.print(f"[dim]SARIF report saved to {output}[/dim]")
        else:
            console.print(result)
    elif format == "markdown":
        reporter = MarkdownReporter()
        result = reporter.generate(findings)
        if output:
            Path(output).write_text(result)
            console.print(f"[dim]Markdown report saved to {output}[/dim]")
        else:
            console.print(result)


def _print_findings_table(findings: list[Finding]) -> None:
    """Print findings as a rich table."""
    table = Table(title="Findings", show_lines=True)
    table.add_column("File", style="cyan", max_width=40)
    table.add_column("Line", style="magenta", justify="right")
    table.add_column("Type", style="yellow")
    table.add_column("Severity", justify="center")
    table.add_column("Source", style="green")
    table.add_column("Match", style="dim", max_width=30)

    severity_styles = {
        "critical": "[bold red]CRITICAL[/bold red]",
        "high": "[red]HIGH[/red]",
        "medium": "[yellow]MEDIUM[/yellow]",
        "low": "[blue]LOW[/blue]",
    }

    # Sort by severity
    severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    sorted_findings = sorted(findings, key=lambda f: severity_order.get(f.severity, 4))

    for finding in sorted_findings:
        source = "[magenta]OCR[/magenta]" if finding.from_ocr else "Text"
        severity_display = severity_styles.get(finding.severity, finding.severity)

        table.add_row(
            str(finding.file_path.name),
            str(finding.line_number),
            finding.pattern_name,
            severity_display,
            source,
            finding.redacted_match(),
        )

    console.print(table)

    # Summary by severity
    console.print("\n[bold]Summary:[/bold]")
    for sev in ["critical", "high", "medium", "low"]:
        count = len([f for f in findings if f.severity == sev])
        if count > 0:
            console.print(f"  {severity_styles.get(sev, sev)}: {count}")


@cli.command()
def patterns() -> None:
    """List all detection patterns."""
    from screenshot_guard.patterns.registry import get_registry

    registry = get_registry()
    stats = registry.get_stats()

    console.print("[bold]Available Pattern Providers:[/bold]\n")

    table = Table()
    table.add_column("Provider", style="cyan")
    table.add_column("Patterns", justify="right")
    table.add_column("Status", style="green")

    for provider, count in stats.items():
        status = "[green]enabled[/green]" if provider in registry.enabled_providers else "[dim]disabled[/dim]"
        table.add_row(provider.upper(), str(count), status)

    console.print(table)
    console.print(f"\n[dim]Total patterns: {sum(stats.values())}[/dim]")


@cli.command()
def version() -> None:
    """Show version information."""
    console.print(f"[bold]Screenshot Guard[/bold] v{__version__}")
    console.print("[dim]Secret Scanner with OCR Superpowers[/dim]")
    console.print("\nhttps://github.com/Keyvanhardani/screenshot-guard")


if __name__ == "__main__":
    cli()

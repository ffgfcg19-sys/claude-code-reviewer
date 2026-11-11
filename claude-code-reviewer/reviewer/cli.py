"""
CLI entry point for Claude Code Reviewer.

Usage:
    python -m reviewer.cli review path/to/file.py
    python -m reviewer.cli review ./src --recursive
    python -m reviewer.cli review file.py --format markdown --output report.md
"""

import sys
import time
from pathlib import Path

import click
from rich.console import Console

from .reviewer import review_file, detect_language, EXTENSION_MAP
from .formatter import print_review

console = Console()

SUPPORTED_EXTENSIONS = set(EXTENSION_MAP.keys())


# ---------------------------------------------------------------------------
# CLI group
# ---------------------------------------------------------------------------

@click.group()
def cli():
    """🔍 Claude Code Reviewer — AI-powered code review in your terminal."""


# ---------------------------------------------------------------------------
# review command
# ---------------------------------------------------------------------------

@cli.command()
@click.argument("path", type=click.Path(exists=True))
@click.option(
    "--model",
    default="claude-opus-4-5",
    show_default=True,
    help="Claude model to use.",
)
@click.option(
    "--lang",
    default=None,
    help="Override auto-detected language.",
)
@click.option(
    "--severity",
    default="low",
    type=click.Choice(["low", "medium", "high", "critical"], case_sensitive=False),
    show_default=True,
    help="Minimum severity level to display.",
)
@click.option(
    "--format",
    "fmt",
    default="text",
    type=click.Choice(["text", "markdown", "json"], case_sensitive=False),
    show_default=True,
    help="Output format.",
)
@click.option(
    "--output",
    default=None,
    type=click.Path(),
    help="Save report to this file instead of stdout.",
)
@click.option(
    "--recursive",
    is_flag=True,
    default=False,
    help="Recursively review all supported files in a directory.",
)
def review(path, model, lang, severity, fmt, output, recursive):
    """Review a source file or directory for bugs, security issues, and style problems."""

    target = Path(path)
    files = []

    if target.is_dir():
        if not recursive:
            console.print(
                "[yellow]Tip:[/] Pass [bold]--recursive[/] to review all files in a directory."
            )
            sys.exit(0)
        for ext in SUPPORTED_EXTENSIONS:
            files.extend(target.rglob(f"*{ext}"))
    else:
        files = [target]

    if not files:
        console.print("[red]No supported source files found.[/]")
        sys.exit(1)

    severity_order = ["low", "medium", "high", "critical"]
    min_sev_index = severity_order.index(severity.lower())

    all_output = []

    for f in files:
        start = time.time()
        console.print(f"\n[bold cyan]Reviewing:[/] {f}")

        try:
            result = review_file(str(f), model=model, language=lang)
        except Exception as exc:
            console.print(f"[red]Error reviewing {f}: {exc}[/]")
            continue

        # Filter issues by minimum severity
        result["issues"] = [
            issue
            for issue in result.get("issues", [])
            if severity_order.index(issue.get("severity", "low").lower()) >= min_sev_index
        ]

        elapsed = time.time() - start
        console.print(f"[dim]Done in {elapsed:.1f}s[/]")

        formatted = print_review(result, fmt=fmt)
        all_output.append(formatted)

    if output and all_output:
        Path(output).write_text("\n\n---\n\n".join(all_output), encoding="utf-8")
        console.print(f"\n[green]Report saved to:[/] {output}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    cli()


if __name__ == "__main__":
    main()

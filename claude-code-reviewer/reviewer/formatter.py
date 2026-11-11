"""
Formatter module — renders review results as rich text, Markdown, or JSON.
"""

import json
from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box
from rich.text import Text

console = Console()

# Severity → colour + emoji mapping
SEVERITY_STYLES = {
    "critical": ("bold red", "🔴"),
    "high": ("bold orange1", "🟠"),
    "medium": ("bold yellow", "🟡"),
    "low": ("bold green", "🟢"),
}


def _severity_badge(severity: str) -> str:
    _, emoji = SEVERITY_STYLES.get(severity.lower(), ("white", "⚪"))
    return f"{emoji} [{severity.upper()}]"


def format_text(review: dict) -> str:
    """Format as a rich terminal output (also returned as plain string)."""
    meta = review.get("_meta", {})
    issues = review.get("issues", [])
    positives = review.get("positives", [])
    score = review.get("score", "?")
    summary = review.get("summary", "")

    lines = []
    lines.append(f"\n🔍 Reviewing: {meta.get('file', 'unknown')}")
    lines.append("━" * 50)
    lines.append(f"\n📋 REVIEW SUMMARY")
    lines.append(f"  File     : {meta.get('file', '?')}")
    lines.append(f"  Language : {meta.get('language', '?')}")
    lines.append(f"  Issues   : {len(issues)} found")
    lines.append(f"  Score    : {score} / 10")
    lines.append(f"\n  {summary}")
    lines.append("\n" + "━" * 50)

    if issues:
        lines.append("")
        for issue in issues:
            sev = issue.get("severity", "low")
            badge = _severity_badge(sev)
            line_ref = f"Line {issue['line']}" if issue.get("line") else "General"
            lines.append(f"{badge} {line_ref} — {issue.get('title', '')}")
            lines.append(f"  {issue.get('description', '')}")
            if issue.get("suggestion"):
                lines.append(f"  💡 Fix: {issue['suggestion']}")
            lines.append("")

    if positives:
        lines.append("✅ What's done well:")
        for p in positives:
            lines.append(f"  • {p}")
        lines.append("")

    tokens = meta.get("input_tokens", 0) + meta.get("output_tokens", 0)
    lines.append("━" * 50)
    lines.append(f"✅ Review complete  |  Tokens used: {tokens}\n")

    return "\n".join(lines)


def format_markdown(review: dict) -> str:
    """Format review as a Markdown document."""
    meta = review.get("_meta", {})
    issues = review.get("issues", [])
    positives = review.get("positives", [])
    score = review.get("score", "?")
    summary = review.get("summary", "")

    md = []
    md.append(f"# Code Review: `{meta.get('file', 'unknown')}`\n")
    md.append(f"**Language:** {meta.get('language', '?')}  ")
    md.append(f"**Score:** {score}/10  ")
    md.append(f"**Issues:** {len(issues)}\n")
    md.append(f"> {summary}\n")

    if issues:
        md.append("## Issues\n")
        for issue in issues:
            sev = issue.get("severity", "low").upper()
            line_ref = f"Line {issue['line']}" if issue.get("line") else "General"
            md.append(f"### `[{sev}]` {issue.get('title', '')} — {line_ref}\n")
            md.append(f"**Category:** {issue.get('category', '?')}  \n")
            md.append(f"{issue.get('description', '')}\n")
            if issue.get("suggestion"):
                md.append(f"\n**Suggestion:** {issue['suggestion']}\n")

    if positives:
        md.append("## ✅ Positives\n")
        for p in positives:
            md.append(f"- {p}")
        md.append("")

    md.append(f"\n---\n*Reviewed with [Claude Code Reviewer](https://github.com) using model `{meta.get('model', '?')}`*")
    return "\n".join(md)


def format_json(review: dict) -> str:
    """Format review as pretty JSON."""
    return json.dumps(review, indent=2)


def print_review(review: dict, fmt: str = "text") -> Optional[str]:
    """
    Print or return a formatted review.

    Args:
        review: Parsed review dict from reviewer.py
        fmt:    One of 'text', 'markdown', 'json'

    Returns:
        Formatted string (always returned, also printed to console).
    """
    if fmt == "json":
        output = format_json(review)
    elif fmt == "markdown":
        output = format_markdown(review)
    else:
        output = format_text(review)

    console.print(output)
    return output

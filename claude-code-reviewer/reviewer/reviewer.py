"""
Core reviewer module — calls the Claude API and parses the response.
"""

import os
import json
from pathlib import Path
from typing import Optional

import anthropic
from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------------------
# Language detection
# ---------------------------------------------------------------------------

EXTENSION_MAP = {
    ".py": "Python",
    ".js": "JavaScript",
    ".ts": "TypeScript",
    ".jsx": "JavaScript (React)",
    ".tsx": "TypeScript (React)",
    ".go": "Go",
    ".rs": "Rust",
    ".java": "Java",
    ".cpp": "C++",
    ".c": "C",
    ".rb": "Ruby",
    ".php": "PHP",
    ".swift": "Swift",
    ".kt": "Kotlin",
    ".cs": "C#",
    ".sh": "Shell",
}


def detect_language(filepath: str) -> str:
    """Return a human-readable language name from a file extension."""
    ext = Path(filepath).suffix.lower()
    return EXTENSION_MAP.get(ext, "Unknown")


# ---------------------------------------------------------------------------
# Review prompt
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """\
You are an expert code reviewer with deep knowledge of software engineering best practices,
security, performance optimisation, and clean code principles.

When reviewing code, examine it for:
1. Bugs and logic errors
2. Security vulnerabilities (hardcoded secrets, injection risks, etc.)
3. Performance issues
4. Code style and readability
5. Missing error handling
6. Refactoring opportunities and design improvements

Always return a JSON object with this exact structure:
{
  "score": <float 0-10>,
  "summary": "<one-sentence overall assessment>",
  "issues": [
    {
      "severity": "<critical|high|medium|low>",
      "line": <int or null>,
      "category": "<bug|security|performance|style|error-handling|refactor>",
      "title": "<short title>",
      "description": "<what is wrong>",
      "suggestion": "<how to fix it>"
    }
  ],
  "positives": ["<thing done well>", ...]
}

Return ONLY the JSON — no markdown fences, no extra text.
"""


def build_user_message(code: str, language: str, filepath: str) -> str:
    return (
        f"Please review the following {language} file: `{filepath}`\n\n"
        f"```{language.lower()}\n{code}\n```"
    )


# ---------------------------------------------------------------------------
# Main review function
# ---------------------------------------------------------------------------

def review_file(
    filepath: str,
    model: str = "claude-opus-4-5",
    language: Optional[str] = None,
) -> dict:
    """
    Send a source file to Claude for code review.

    Args:
        filepath: Path to the source file.
        model:    Anthropic model identifier.
        language: Override auto-detected language (optional).

    Returns:
        Parsed review dict (see SYSTEM_PROMPT for schema).
    """
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "ANTHROPIC_API_KEY is not set. "
            "Copy .env.example to .env and add your key."
        )

    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {filepath}")

    code = path.read_text(encoding="utf-8")
    lang = language or detect_language(filepath)

    client = anthropic.Anthropic(api_key=api_key)

    message = client.messages.create(
        model=model,
        max_tokens=2048,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": build_user_message(code, lang, filepath),
            }
        ],
    )

    raw = message.content[0].text.strip()

    try:
        result = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Claude returned unexpected output (not valid JSON):\n{raw}"
        ) from exc

    # Attach metadata
    result["_meta"] = {
        "file": filepath,
        "language": lang,
        "model": model,
        "input_tokens": message.usage.input_tokens,
        "output_tokens": message.usage.output_tokens,
    }

    return result

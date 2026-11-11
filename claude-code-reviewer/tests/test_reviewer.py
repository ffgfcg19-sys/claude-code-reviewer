"""
Tests for the Claude Code Reviewer.

Run with:
    pytest tests/
"""

import json
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch

from reviewer.reviewer import detect_language, build_user_message
from reviewer.formatter import format_text, format_markdown, format_json


# ---------------------------------------------------------------------------
# Language detection
# ---------------------------------------------------------------------------

class TestDetectLanguage:
    def test_python(self):
        assert detect_language("script.py") == "Python"

    def test_javascript(self):
        assert detect_language("app.js") == "JavaScript"

    def test_typescript(self):
        assert detect_language("index.ts") == "TypeScript"

    def test_unknown_extension(self):
        assert detect_language("file.xyz") == "Unknown"

    def test_case_insensitive(self):
        assert detect_language("SCRIPT.PY") == "Python"


# ---------------------------------------------------------------------------
# Message builder
# ---------------------------------------------------------------------------

class TestBuildUserMessage:
    def test_contains_language(self):
        msg = build_user_message("x = 1", "Python", "test.py")
        assert "Python" in msg

    def test_contains_code(self):
        msg = build_user_message("x = 1", "Python", "test.py")
        assert "x = 1" in msg

    def test_contains_filepath(self):
        msg = build_user_message("x = 1", "Python", "test.py")
        assert "test.py" in msg


# ---------------------------------------------------------------------------
# Formatters (no API calls)
# ---------------------------------------------------------------------------

SAMPLE_REVIEW = {
    "score": 6.5,
    "summary": "Decent code with a few issues.",
    "issues": [
        {
            "severity": "critical",
            "line": 12,
            "category": "security",
            "title": "Hardcoded API key",
            "description": "API key is embedded in source code.",
            "suggestion": "Use os.getenv('API_KEY') instead.",
        },
        {
            "severity": "medium",
            "line": None,
            "category": "style",
            "title": "Missing docstrings",
            "description": "Several functions lack docstrings.",
            "suggestion": "Add docstrings to all public functions.",
        },
    ],
    "positives": ["Good use of context managers", "Consistent naming"],
    "_meta": {
        "file": "examples/sample.py",
        "language": "Python",
        "model": "claude-opus-4-5",
        "input_tokens": 500,
        "output_tokens": 300,
    },
}


class TestFormatText:
    def test_contains_score(self):
        out = format_text(SAMPLE_REVIEW)
        assert "6.5" in out

    def test_contains_severity(self):
        out = format_text(SAMPLE_REVIEW)
        assert "CRITICAL" in out

    def test_contains_positives(self):
        out = format_text(SAMPLE_REVIEW)
        assert "context managers" in out


class TestFormatMarkdown:
    def test_starts_with_heading(self):
        out = format_markdown(SAMPLE_REVIEW)
        assert out.startswith("# Code Review")

    def test_contains_issues(self):
        out = format_markdown(SAMPLE_REVIEW)
        assert "Hardcoded API key" in out


class TestFormatJson:
    def test_valid_json(self):
        out = format_json(SAMPLE_REVIEW)
        parsed = json.loads(out)
        assert parsed["score"] == 6.5

    def test_issues_present(self):
        out = format_json(SAMPLE_REVIEW)
        parsed = json.loads(out)
        assert len(parsed["issues"]) == 2


# ---------------------------------------------------------------------------
# review_file — mocked API call
# ---------------------------------------------------------------------------

class TestReviewFile:
    @patch("reviewer.reviewer.anthropic.Anthropic")
    @patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test-key"})
    def test_returns_dict(self, mock_anthropic):
        mock_response = MagicMock()
        mock_response.content = [
            MagicMock(
                text=json.dumps(
                    {
                        "score": 8.0,
                        "summary": "Good code.",
                        "issues": [],
                        "positives": ["Clean structure"],
                    }
                )
            )
        ]
        mock_response.usage.input_tokens = 100
        mock_response.usage.output_tokens = 50
        mock_anthropic.return_value.messages.create.return_value = mock_response

        from reviewer.reviewer import review_file

        result = review_file("examples/sample.py")
        assert isinstance(result, dict)
        assert result["score"] == 8.0
        assert "_meta" in result

    @patch.dict("os.environ", {}, clear=True)
    def test_missing_api_key_raises(self):
        from reviewer.reviewer import review_file

        with pytest.raises(EnvironmentError, match="ANTHROPIC_API_KEY"):
            review_file("examples/sample.py")

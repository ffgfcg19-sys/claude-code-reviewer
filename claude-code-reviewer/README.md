# 🔍 Claude Code Reviewer

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python)](https://python.org)
[![Claude API](https://img.shields.io/badge/Powered%20by-Claude%20API-orange)](https://anthropic.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

> An intelligent CLI code reviewer powered by Claude. Drop any Python or JavaScript file and get instant, actionable feedback — bugs, style issues, security risks, and refactoring suggestions.

---

## ✨ Features

- 🐛 **Bug Detection** — Spots logic errors, off-by-one errors, and runtime exceptions before you do
- 🔐 **Security Analysis** — Flags hardcoded secrets, SQL injection risks, and unsafe patterns
- 🎨 **Style & Best Practices** — Checks PEP 8 compliance, naming conventions, and code clarity
- ♻️ **Refactoring Suggestions** — Recommends cleaner patterns and idiomatic rewrites
- 📊 **Severity Scoring** — Each issue is rated Critical / High / Medium / Low
- 🗂️ **Multi-file support** — Review entire directories at once
- 💾 **Export reports** — Save reviews as Markdown or JSON

---

## 📸 Demo

```
$ python -m reviewer.cli review examples/sample.py

🔍 Reviewing: examples/sample.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 REVIEW SUMMARY
  File     : examples/sample.py
  Language : Python
  Issues   : 4 found (1 Critical, 1 High, 2 Medium)
  Score    : 6.5 / 10

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔴 [CRITICAL] Line 12 — Hardcoded API Key
  Found: api_key = "sk-abc123..."
  Fix:   Use environment variables: os.getenv("API_KEY")

🟠 [HIGH] Line 27 — Bare except clause
  Found: except:
  Fix:   Catch specific exceptions, e.g. except ValueError:

🟡 [MEDIUM] Line 34 — Mutable default argument
  Found: def process(data, results=[]):
  Fix:   Use None as default and initialise inside function

🟡 [MEDIUM] Line 41 — Missing return type hint
  Suggestion: Add -> dict to improve readability

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Review complete in 2.3s
```

---

## 🚀 Quick Start

### 1. Clone & Install

```bash
git clone https://github.com/YOUR_USERNAME/claude-code-reviewer.git
cd claude-code-reviewer
pip install -r requirements.txt
```

### 2. Add your API key

```bash
cp .env.example .env
# Edit .env and paste your Anthropic API key
```

### 3. Run a review

```bash
# Review a single file
python -m reviewer.cli review path/to/your_file.py

# Review all Python files in a directory
python -m reviewer.cli review ./src --recursive

# Export report to Markdown
python -m reviewer.cli review my_script.py --output report.md

# Export as JSON (great for CI/CD pipelines)
python -m reviewer.cli review my_script.py --format json --output review.json
```

---

## ⚙️ Configuration

You can customise the review behaviour with flags:

| Flag | Description | Default |
|------|-------------|---------|
| `--model` | Claude model to use | `claude-opus-4-5` |
| `--lang` | Force a language (`python`, `javascript`) | auto-detect |
| `--severity` | Minimum severity to show (`low`, `medium`, `high`, `critical`) | `low` |
| `--format` | Output format (`text`, `markdown`, `json`) | `text` |
| `--output` | Save report to file | stdout |
| `--recursive` | Recursively review directories | `False` |

---

## 🏗️ Project Structure

```
claude-code-reviewer/
├── reviewer/
│   ├── __init__.py      # Package entry point
│   ├── cli.py           # Click-based CLI interface
│   ├── reviewer.py      # Core Claude API integration
│   └── formatter.py     # Output formatters (text, markdown, JSON)
├── examples/
│   └── sample.py        # Example file with intentional issues to demo the tool
├── tests/
│   └── test_reviewer.py # Unit tests
├── .env.example         # Environment variable template
├── requirements.txt
└── setup.py
```

---

## 🔧 Requirements

- Python 3.8+
- Anthropic API key ([get one here](https://console.anthropic.com/))

---

## 🤝 Contributing

Pull requests are welcome! Please open an issue first to discuss what you'd like to change.

---

## 📄 License

MIT © 2024

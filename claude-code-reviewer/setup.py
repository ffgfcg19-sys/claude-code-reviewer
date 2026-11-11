from setuptools import setup, find_packages

setup(
    name="claude-code-reviewer",
    version="1.0.0",
    description="AI-powered code reviewer using Claude",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "anthropic>=0.25.0",
        "click>=8.1.0",
        "python-dotenv>=1.0.0",
        "rich>=13.0.0",
    ],
    entry_points={
        "console_scripts": [
            "code-review=reviewer.cli:main",
        ],
    },
)

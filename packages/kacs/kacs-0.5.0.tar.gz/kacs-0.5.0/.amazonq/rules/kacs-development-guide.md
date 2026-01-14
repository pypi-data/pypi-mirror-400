# kacs Development Guide

**kacs** (Keep a Changelog, Stupid!) is a minimal Python CLI tool that generates changelogs from git commit messages using LLM analysis.

## Technical Specifications

- **Core Function**: Parse git commit messages between specified tags, analyze with LLM, output structured changelog
- **Runtime Target**: CI/CD pipelines and automated release workflows
- **Architecture**: Single-module Python package with CLI entry point
- **LLM Integration**: Use ask2api library exclusively for structured LLM responses
- **Output Specification**: Must generate valid Keep a Changelog format (https://keepachangelog.com/)

## Implementation Requirements

### Minimal Dependencies
- Standard library: `subprocess`, `argparse`, `json`, `os`
- External: `ask2api` (for LLM structured output)
- No additional dependencies unless absolutely necessary

### CLI Interface Design
```bash
kacs --from-tag v1.0.0 --to-tag v1.1.0 [--output changelog.md]
```

### Core Module Structure
```python
# kacs/main.py or kacs.py
def extract_commits(from_tag: str, to_tag: str) -> list[str]:
    """Extract commit messages between git tags using subprocess"""

def analyze_commits(commits: list[str]) -> dict:
    """Use ask2api to categorize commits into changelog sections"""

def generate_changelog(analysis: dict, version: str) -> str:
    """Format analysis into Keep a Changelog format"""
```

### ask2api Integration Pattern
- Define JSON schema for changelog structure (Added, Changed, Fixed, etc.)
- Pass commit messages as prompt to ask2api
- Use structured output to categorize commits
- Example schema:
```json
{
  "type": "object",
  "properties": {
    "added": {"type": "array", "items": {"type": "string"}},
    "changed": {"type": "array", "items": {"type": "string"}},
    "fixed": {"type": "array", "items": {"type": "string"}}
  }
}
```

### ask2api Usage Example
```python
import subprocess
import json
from ask2api import generate_api_response, Config

def analyze_commits(commits: list[str]) -> dict:
    # Prepare commit messages as prompt
    prompt = f"Analyze these git commits and categorize them:\n\n" + "\n".join(commits)

    # Define changelog schema
    schema = {
        "type": "object",
        "properties": {
            "added": {"type": "array", "items": {"type": "string"}},
            "changed": {"type": "array", "items": {"type": "string"}},
            "fixed": {"type": "array", "items": {"type": "string"}},
            "deprecated": {"type": "array", "items": {"type": "string"}},
            "removed": {"type": "array", "items": {"type": "string"}},
            "security": {"type": "array", "items": {"type": "string"}}
        },
        "required": ["added", "changed", "fixed"]
    }

    # Get structured response from LLM
    config = Config.from_env()  # Uses ASK2API_API_KEY or OPENAI_API_KEY
    result = generate_api_response(prompt, schema, config)

    return result
```

## Development Constraints

- **Code Style**: Follow existing minimal patterns, avoid over-engineering
- **Error Handling**: Fail fast with clear error messages
- **Git Operations**: Use `subprocess` with `git` commands, no GitPython dependency
- **Testing**: Test with real git repositories containing actual tags
- **Output**: Write to stdout by default, file output optional

## Implementation Priority

1. Git tag enumeration and commit extraction
2. ask2api integration with changelog schema
3. Keep a Changelog format generation
4. CLI argument parsing and main entry point
5. Error handling and edge cases

## Code Generation Guidelines

- Use type hints for all function signatures
- Keep functions pure and testable
- Minimize external API calls (batch commit analysis)
- Handle git repository edge cases (no tags, invalid ranges)
- Ensure generated changelog adheres strictly to Keep a Changelog format

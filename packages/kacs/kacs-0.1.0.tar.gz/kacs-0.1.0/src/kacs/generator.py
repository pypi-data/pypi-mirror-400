"""LLM-powered changelog generation for kacs."""

from typing import List, Dict
from ask2api import generate_api_response, Config


CHANGELOG_SCHEMA = {
    "type": "object",
    "properties": {
        "added": {"type": "array", "items": {"type": "string"}},
        "changed": {"type": "array", "items": {"type": "string"}},
        "fixed": {"type": "array", "items": {"type": "string"}},
        "deprecated": {"type": "array", "items": {"type": "string"}},
        "removed": {"type": "array", "items": {"type": "string"}},
        "security": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["added", "changed", "fixed"],
}


def analyze_commits(commits: List[str]) -> Dict:
    """Use ask2api to categorize commits into changelog sections."""
    if not commits:
        return {
            "added": [],
            "changed": [],
            "fixed": [],
            "deprecated": [],
            "removed": [],
            "security": [],
        }

    prompt = (
        "Analyze these git commits and categorize them into changelog sections:\n\n"
        + "\n".join(commits)
    )

    try:
        config = Config.from_env()
        result = generate_api_response(prompt, CHANGELOG_SCHEMA, config)
        return result
    except Exception as e:
        raise RuntimeError(f"Failed to analyze commits with LLM: {e}")


def generate_changelog(analysis: Dict, version: str, release_date: str) -> str:
    """Format analysis into Keep a Changelog format."""
    clean_version = version.lstrip("v")
    changelog = f"## [{clean_version}] - {release_date}\n\n"

    sections = [
        ("Added", analysis.get("added", [])),
        ("Changed", analysis.get("changed", [])),
        ("Deprecated", analysis.get("deprecated", [])),
        ("Removed", analysis.get("removed", [])),
        ("Fixed", analysis.get("fixed", [])),
        ("Security", analysis.get("security", [])),
    ]

    for section_name, items in sections:
        if items:
            changelog += f"### {section_name}\n"
            for item in items:
                changelog += f"- {item}\n"
            changelog += "\n"

    return changelog.rstrip() + "\n"

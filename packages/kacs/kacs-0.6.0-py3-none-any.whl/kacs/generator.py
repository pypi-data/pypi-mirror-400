"""LLM-powered changelog generation for kacs."""

import os
from typing import List, Dict, Optional
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


def analyze_commits(
    commits: List[Dict[str, str]],
    language: str = "en",
    instructions: Optional[str] = None,
) -> Dict:
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

    # Extract messages from commit dicts
    messages = [c["message"] if isinstance(c, dict) else c for c in commits]

    lang_instruction = f" Respond in {language}." if language != "en" else ""
    extra_instruction = f" {instructions}" if instructions else ""
    prompt = (
        f"Analyze these git commits and categorize them into changelog sections.{lang_instruction}{extra_instruction}\n\n"
        + "\n".join(messages)
    )

    try:
        config = Config.from_env()
        result = generate_api_response(prompt, CHANGELOG_SCHEMA, config)
        return result
    except Exception as e:
        raise RuntimeError(f"Failed to analyze commits with LLM: {e}")


def generate_changelog(
    analysis: Dict,
    version: str,
    release_date: str,
    template: Optional[str] = None,
    custom_template: Optional[str] = None,
    include_links: bool = False,
    repo_url: Optional[str] = None,
    from_tag: str = "",
    commits: Optional[List[Dict[str, str]]] = None,
) -> str:
    """Format analysis into changelog format.

    If template is provided, uses template system. Otherwise falls back to
    Keep a Changelog format for backward compatibility.
    """
    if template or custom_template:
        from .renderer import render_changelog

        return render_changelog(
            analysis,
            version,
            release_date,
            template or "keepachangelog",
            custom_template,
            include_links,
            repo_url,
            from_tag,
            commits,
        )

    # Backward compatible: Keep a Changelog format
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


def append_to_changelog(filepath: str, new_entry: str) -> None:
    """Append new changelog entry to existing file."""
    if not os.path.exists(filepath):
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(new_entry)
        return

    with open(filepath, "r", encoding="utf-8") as f:
        existing_content = f.read().strip()

    lines = existing_content.split("\n")
    insert_idx = len(lines)

    # Find insertion point after [Unreleased] or before first version entry
    for i, line in enumerate(lines):
        if line.startswith("## [Unreleased]"):
            # Skip [Unreleased] section and find next ## [ or end
            for j in range(i + 1, len(lines)):
                if lines[j].startswith("## [") and "Unreleased" not in lines[j]:
                    insert_idx = j
                    break
            break
        elif line.startswith("## ["):
            insert_idx = i
            break

    new_lines = lines[:insert_idx] + [new_entry.rstrip()] + [""] + lines[insert_idx:]

    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(new_lines))

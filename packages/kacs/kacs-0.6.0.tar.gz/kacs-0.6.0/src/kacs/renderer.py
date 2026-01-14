"""Template rendering for kacs."""

from pathlib import Path
from typing import Dict, List, Optional

try:
    from jinja2 import Environment, FileSystemLoader, Template
except ImportError:
    Environment = FileSystemLoader = Template = None


def get_template_path(template_name: str) -> Path:
    """Get path to built-in template."""
    templates_dir = Path(__file__).parent / "templates"
    return templates_dir / f"{template_name}.j2"


def load_template(template_name: str, custom_path: Optional[str] = None) -> "Template":
    """Load template by name or custom path."""
    if Template is None:
        raise RuntimeError("jinja2 is required for template rendering")

    # Custom template path
    if custom_path:
        with open(custom_path, "r", encoding="utf-8") as f:
            return Template(f.read())

    # Built-in template
    template_path = get_template_path(template_name)
    if not template_path.exists():
        raise ValueError(f"Template '{template_name}' not found")

    with open(template_path, "r", encoding="utf-8") as f:
        return Template(f.read())


def render_changelog(
    analysis: Dict,
    version: str,
    date: str,
    template: str = "keepachangelog",
    custom_template: Optional[str] = None,
    include_links: bool = False,
    repo_url: Optional[str] = None,
    from_tag: str = "",
    commits_with_hash: Optional[List[Dict[str, str]]] = None,
) -> str:
    """Render changelog using template."""
    tmpl = load_template(template, custom_template)

    # Prepare sections with commit hashes
    sections = {}
    commit_map = {c["message"]: c.get("hash", "") for c in (commits_with_hash or [])}

    for key in ["added", "changed", "fixed", "deprecated", "removed", "security"]:
        items = analysis.get(key, [])
        sections[key] = [
            {"message": msg, "hash": commit_map.get(msg, "")} for msg in items
        ]

    # Default section names
    section_names = {
        "added": "Added",
        "changed": "Changed",
        "fixed": "Fixed",
        "deprecated": "Deprecated",
        "removed": "Removed",
        "security": "Security",
    }

    clean_version = version.lstrip("v")

    context = {
        "version": clean_version,
        "date": date,
        "sections": sections,
        "section_names": section_names,
        "include_links": include_links,
        "repo_url": repo_url or "",
        "from_tag": from_tag,
        "to_tag": version,
    }

    return tmpl.render(**context)

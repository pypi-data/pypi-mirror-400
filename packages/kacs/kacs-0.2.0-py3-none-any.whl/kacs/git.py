"""Git operations for kacs."""

import subprocess
from typing import List


def is_git_repository() -> bool:
    """Check if current directory is a git repository."""
    try:
        subprocess.run(
            ["git", "rev-parse", "--git-dir"],
            check=True,
            capture_output=True,
            text=True,
        )
        return True
    except subprocess.CalledProcessError:
        return False


def tag_exists(tag: str) -> bool:
    """Check if a git tag exists."""
    try:
        subprocess.run(
            ["git", "rev-parse", f"refs/tags/{tag}"],
            check=True,
            capture_output=True,
            text=True,
        )
        return True
    except subprocess.CalledProcessError:
        return False


def extract_commits(from_tag: str, to_tag: str) -> List[str]:
    """Extract commit messages between git tags."""
    if not is_git_repository():
        raise RuntimeError("Not in a git repository")

    if not tag_exists(from_tag):
        raise ValueError(f"Tag '{from_tag}' does not exist")

    if not tag_exists(to_tag):
        raise ValueError(f"Tag '{to_tag}' does not exist")

    try:
        result = subprocess.run(
            ["git", "log", f"{from_tag}..{to_tag}", "--pretty=format:%B%n---"],
            check=True,
            capture_output=True,
            text=True,
        )
        commits = [
            commit.strip() for commit in result.stdout.split("---") if commit.strip()
        ]
        return commits
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to extract commits: {e}")

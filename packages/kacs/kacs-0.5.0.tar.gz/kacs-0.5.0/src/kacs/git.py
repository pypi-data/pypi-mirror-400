"""Git operations for kacs."""

import subprocess
from typing import List, Dict, Optional


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


def ref_exists(ref: str) -> bool:
    """Check if a git reference (tag, branch, or HEAD) exists."""
    try:
        subprocess.run(
            ["git", "rev-parse", "--verify", ref],
            check=True,
            capture_output=True,
            text=True,
        )
        return True
    except subprocess.CalledProcessError:
        return False


def get_repository_url() -> Optional[str]:
    """Extract repository URL from git remote."""
    try:
        result = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            check=True,
            capture_output=True,
            text=True,
        )
        url = result.stdout.strip()
        # Normalize URL: remove .git suffix, convert SSH to HTTPS
        if url.endswith(".git"):
            url = url[:-4]
        if url.startswith("git@github.com:"):
            url = url.replace("git@github.com:", "https://github.com/")
        if url.startswith("git@gitlab.com:"):
            url = url.replace("git@gitlab.com:", "https://gitlab.com/")
        return url
    except subprocess.CalledProcessError:
        return None


def extract_commits(from_ref: str, to_ref: str) -> List[Dict[str, str]]:
    """Extract commit messages and hashes between git references (tags, branches, or HEAD)."""
    if not is_git_repository():
        raise RuntimeError("Not in a git repository")

    if not ref_exists(from_ref):
        raise ValueError(f"Reference '{from_ref}' does not exist")

    if not ref_exists(to_ref):
        raise ValueError(f"Reference '{to_ref}' does not exist")

    try:
        result = subprocess.run(
            ["git", "log", f"{from_ref}..{to_ref}", "--pretty=format:%H|||%B|||---"],
            check=True,
            capture_output=True,
            text=True,
        )
        commits = []
        for entry in result.stdout.split("|||---"):
            entry = entry.strip()
            if not entry:
                continue
            parts = entry.split("|||", 1)
            if len(parts) == 2:
                commits.append({"hash": parts[0].strip(), "message": parts[1].strip()})
        return commits
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to extract commits: {e}")

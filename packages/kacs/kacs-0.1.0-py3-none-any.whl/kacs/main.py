"""kacs - Keep a changelog, stupid!"""

import argparse
import sys
from datetime import date
from .git import extract_commits
from .generator import analyze_commits, generate_changelog


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Generate changelogs from git commit messages using LLM.",
        prog="kacs",
    )
    parser.add_argument(
        "--from-tag", required=True, help="Starting git tag for changelog generation"
    )
    parser.add_argument(
        "--to-tag", required=True, help="Ending git tag for changelog generation"
    )
    parser.add_argument("--output", help="Output file path (default: stdout)")
    parser.add_argument(
        "--date", help="Release date (YYYY-MM-DD format, default: today)"
    )

    args = parser.parse_args()

    try:
        # Extract commits between tags
        commits = extract_commits(args.from_tag, args.to_tag)

        if not commits:
            print(
                f"No commits found between {args.from_tag} and {args.to_tag}",
                file=sys.stderr,
            )
            sys.exit(1)

        # Analyze commits with LLM
        analysis = analyze_commits(commits)

        # Get release date
        release_date = args.date if args.date else date.today().isoformat()

        # Generate changelog
        changelog = generate_changelog(analysis, args.to_tag, release_date)

        # Output to file or stdout
        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(changelog)
            print(f"Changelog written to {args.output}")
        else:
            print(changelog, end="")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

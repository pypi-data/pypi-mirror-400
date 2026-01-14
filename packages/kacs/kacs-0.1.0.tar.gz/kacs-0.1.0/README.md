# kacs

[![CI](https://github.com/atasoglu/kacs/actions/workflows/pre-commit.yml/badge.svg)](https://github.com/atasoglu/kacs/actions/workflows/pre-commit.yml)
[![PyPI version](https://img.shields.io/pypi/v/kacs)](https://pypi.org/project/kacs/)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Keep a changelog, stupid!**

A minimal Python CLI tool that generates changelogs from git commit messages using LLM analysis. Perfect for CI/CD pipelines and automated release workflows.

## Features

- 🚀 **Minimal dependencies** - Only requires `ask2api` + Python stdlib
- 📝 **Keep a Changelog format** - Generates valid [keepachangelog.com](https://keepachangelog.com/) format
- 🤖 **LLM-powered analysis** - Automatically categorizes commits into Added, Changed, Fixed, etc.
- ⚡ **CI/CD ready** - Fast execution suitable for automated workflows
- 🎯 **Git tag based** - Extract commits between any two git tags

## Installation

```bash
pip install kacs
```

## Setup

Set your API key as an environment variable:

```bash
export ASK2API_API_KEY="your-api-key"
# or
export OPENAI_API_KEY="your-openai-key"
```

## Usage

### Basic Usage

```bash
# Generate changelog between two tags
kacs --from-tag v1.0.0 --to-tag v1.1.0

# With custom date
kacs --from-tag v1.0.0 --to-tag v1.1.0 --date 2017-07-17

# Save to file
kacs --from-tag v1.0.0 --to-tag v1.1.0 --output CHANGELOG.md
```

### Example Output

```markdown
## [1.1.0] - 2024-01-15

### Added
- New user authentication system
- Support for multiple database backends

### Changed
- Improved error handling in API endpoints
- Updated documentation structure

### Fixed
- Fixed memory leak in background tasks
- Resolved issue with concurrent requests
```

### CI/CD Integration

```yaml
# GitHub Actions example
- name: Generate Changelog
  run: |
    pip install kacs
    kacs --from-tag ${{ github.event.release.tag_name }} --to-tag HEAD --output CHANGELOG.md
  env:
    ASK2API_API_KEY: ${{ secrets.ASK2API_API_KEY }}
```

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## Links

- [PyPI Package](https://pypi.org/project/kacs/)
- [GitHub Repository](https://github.com/atasoglu/kacs)
- [Keep a Changelog](https://keepachangelog.com/)

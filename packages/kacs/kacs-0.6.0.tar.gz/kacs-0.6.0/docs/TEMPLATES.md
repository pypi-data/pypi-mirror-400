# Template System Documentation

kacs supports multiple changelog formats through a flexible template system powered by Jinja2.

## Built-in Templates

### 1. Keep a Changelog (default)
Standard format following [keepachangelog.com](https://keepachangelog.com/) specification.

```bash
kacs --from-tag v1.0.0 --to-tag v1.1.0 --template keepachangelog
```

**Output:**
```markdown
## [1.1.0] - 2024-01-15

### Added
- New feature A
- New feature B

### Fixed
- Bug fix C
```

### 2. GitHub Release Notes
GitHub-style release notes with emoji icons.

```bash
kacs --from-tag v1.0.0 --to-tag v1.1.0 --template github
```

**Output:**
```markdown
## What's Changed in 1.1.0

### ✨ New Features
* New feature A
* New feature B

### 🐛 Bug Fixes
* Bug fix C

**Full Changelog**: https://github.com/user/repo/compare/v1.0.0...v1.1.0
```

### 3. GitLab Format
GitLab-style changelog format.

```bash
kacs --from-tag v1.0.0 --to-tag v1.1.0 --template gitlab
```

**Output:**
```markdown
## 1.1.0 (2024-01-15)

#### Added
- New feature A
- New feature B

#### Fixed
- Bug fix C
```

### 4. Simple Format
Minimal format with symbols.

```bash
kacs --from-tag v1.0.0 --to-tag v1.1.0 --template simple
```

**Output:**
```
# 1.1.0 - 2024-01-15
+ New feature A
+ New feature B
* Bug fix C
```

## Custom Templates

Create your own Jinja2 template for complete control over the output format.

### Creating a Custom Template

1. Create a `.j2` file with your template:

```jinja2
# Release {{ version }}
Released on {{ date }}

{% if sections.added %}
## New Stuff
{% for item in sections.added %}
- {{ item.message }}
{% endfor %}
{% endif %}

{% if sections.fixed %}
## Fixes
{% for item in sections.fixed %}
- {{ item.message }}
{% endfor %}
{% endif %}
```

2. Use it with kacs:

```bash
kacs --from-tag v1.0.0 --to-tag v1.1.0 --custom-template ./my-template.j2
```

### Available Template Variables

| Variable | Type | Description |
|----------|------|-------------|
| `version` | string | Version number (without 'v' prefix) |
| `date` | string | Release date (YYYY-MM-DD) |
| `sections` | dict | Categorized commits |
| `sections.added` | list | Added features |
| `sections.changed` | list | Changed features |
| `sections.fixed` | list | Bug fixes |
| `sections.deprecated` | list | Deprecated features |
| `sections.removed` | list | Removed features |
| `sections.security` | list | Security fixes |
| `section_names` | dict | Customized section names |
| `include_links` | bool | Whether to include commit links |
| `repo_url` | string | Repository URL |
| `from_tag` | string | Starting tag |
| `to_tag` | string | Ending tag |

### Commit Item Structure

Each item in `sections.*` is a dict with:
- `message`: Commit message (string)
- `hash`: Commit hash (string, may be empty)

Example:
```jinja2
{% for item in sections.added %}
- {{ item.message }}
  {% if include_links and item.hash %}
  Commit: [{{ item.hash[:7] }}]({{ repo_url }}/commit/{{ item.hash }})
  {% endif %}
{% endfor %}
```

## Commit Links

Enable commit links to include references to specific commits in your changelog.

### Auto-detection

```bash
kacs --from-tag v1.0.0 --to-tag v1.1.0 --include-links
```

kacs will automatically detect your repository URL from `git remote`.

### Manual URL

```bash
kacs --from-tag v1.0.0 --to-tag v1.1.0 --include-links --repo-url https://github.com/user/repo
```

### Example Output with Links

```markdown
### Added
- New authentication system ([abc1234](https://github.com/user/repo/commit/abc1234))
- Support for PostgreSQL ([def5678](https://github.com/user/repo/commit/def5678))
```

## Troubleshooting

### Template Not Found
- Ensure template name is spelled correctly: `keepachangelog`, `github`, `gitlab`, or `simple`
- For custom templates, verify file path exists

### Commit Links Not Working
- Verify you're in a git repository with a remote
- Use `--repo-url` to specify URL manually
- Check repository URL format (GitHub/GitLab supported)

1. **Consistency**: Choose one template and stick with it across releases
2. **Commit Links**: Enable for better traceability in large projects
3. **Custom Templates**: Keep templates simple and readable
4. **Version Control**: Store custom templates in your repository

## Examples

### Corporate Style
```jinja2
# {{ version }} Release Notes
**Release Date:** {{ date }}

{% if sections.added or sections.changed %}
## Features & Improvements
{% for item in sections.added %}
- [NEW] {{ item.message }}
{% endfor %}
{% for item in sections.changed %}
- [IMPROVED] {{ item.message }}
{% endfor %}
{% endif %}

{% if sections.fixed %}
## Bug Fixes
{% for item in sections.fixed %}
- {{ item.message }}
{% endfor %}
{% endif %}
```

### Emoji Style
```jinja2
## {{ version }} ({{ date }})

{% for item in sections.added %}
✨ {{ item.message }}
{% endfor %}
{% for item in sections.fixed %}
🐛 {{ item.message }}
{% endfor %}
{% for item in sections.security %}
🔒 {{ item.message }}
{% endfor %}
```

### Detailed Style with Links
```jinja2
# Version {{ version }}
*Released: {{ date }}*

---

{% if sections.added %}
### 🎉 New Features
{% for item in sections.added %}
**{{ item.message }}**
{% if include_links and item.hash %}
> Commit: [`{{ item.hash[:7] }}`]({{ repo_url }}/commit/{{ item.hash }})
{% endif %}

{% endfor %}
{% endif %}
```

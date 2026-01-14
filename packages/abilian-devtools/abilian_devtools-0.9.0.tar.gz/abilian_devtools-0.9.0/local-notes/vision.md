# ADT Seed Vision Document

## Overview

Transform `adt seed` from a simple file copier into a flexible, profile-based project scaffolding system. Unlike Cookiecutter (which creates new projects), ADT Seed **augments existing projects** with configuration files, scripts, and best practices—and keeps them updated over time.

### Design Philosophy

1. **Augment, don't create** — Works on existing projects, not just new ones
2. **Layered profiles** — Compose configurations from base to specialized
3. **Personal preferences** — Your profiles, your way, stored where you want
4. **Transparent templates** — Jinja2 with explicit `.j2` extension
5. **Executable profiles** — Scripts automate post-seed setup tasks
6. **Non-destructive by default** — Never overwrite without explicit consent

---

## Architecture

### Configuration Hierarchy

```
~/.config/adt/
├── config.toml              # Global ADT configuration
└── profiles/                # Local profile storage (optional)
    ├── python/
    ├── web/
    └── ...
```

`~/.config/adt/config.toml` may also point to local directories countaining the profiles, or map profile names to git repositories.

Let's focus on local profiles first.

### Profile Structure

A profile is a directory containing:

```
my-profile/
├── profile.toml             # Profile metadata and configuration
├── templates/               # Files to copy/render
│   ├── ruff.toml            # Static file (copied as-is)
│   ├── Makefile.j2          # Jinja2 template (rendered)
│   ├── pyproject.toml.j2
│   └── .github/
│       └── workflows/
│           └── ci.yml.j2
└── scripts/                 # Post-seed scripts
    ├── 01-install-deps.sh
    └── 02-setup-hooks.sh
```

---

## Configuration Files

### Global Config (`~/.config/adt/config.toml`)

```toml
# Default profile when none specified
default_profile = "python"

# Profile sources - local paths or git URLs
[sources]
python = "~/.config/adt/profiles/python"
web = "~/.config/adt/profiles/web"
company = "git@github.com:mycompany/adt-profiles.git#main:company"
personal = "https://github.com/myuser/dotfiles.git#main:adt-profiles/python"

# Global variable defaults (lowest priority)
[variables]
author = "Your Name"
email = "you@example.com"
license = "MIT"
github_username = "yourusername"

# Behavior settings
[settings]
# Ask before running scripts
confirm_scripts = true
# Cache git profiles locally
cache_git_profiles = true
cache_dir = "~/.cache/adt/profiles"
```

### Profile Config (`profile.toml`)

```toml
[profile]
name = "python"
description = "Modern Python project with ruff, ty, pytest, and uv"
version = "1.0.0"

# Profile inheritance - applied in order (base first)
extends = []
# extends = ["base"]
# extends = ["python", "cli"]

[variables]
# Default values for this profile's templates
python_version = "3.12"
min_python = "3.10"
use_src_layout = true

# Variable descriptions (for interactive mode / documentation)
[variables.meta]
python_version.description = "Target Python version"
python_version.type = "string"
python_version.choices = ["3.10", "3.11", "3.12", "3.13"]

[files]
# Optional: explicit file mappings (default: copy all from templates/)
# Format: "source" = "destination" or "source" = { dest = "...", condition = "..." }

# Conditional files
"templates/.github/workflows/ci.yml.j2" = { dest = ".github/workflows/ci.yml", condition = "use_github_actions" }
"templates/docker/Dockerfile.j2" = { dest = "Dockerfile", condition = "use_docker" }

# File rename
"templates/gitignore" = ".gitignore"

[scripts]
# Scripts to run after files are seeded
# Paths relative to profile directory
post_seed = [
    "scripts/01-install-deps.sh",
    "scripts/02-setup-hooks.sh",
]

# Environment variables for scripts
[scripts.env]
PYTHON_VERSION = "{{ python_version }}"

[conditions]
# Define conditions based on project state
has_tests = "path_exists('tests/')"
has_src = "path_exists('src/')"
use_github_actions = "path_exists('.github/')"
use_docker = "var('use_docker', false)"
is_package = "pyproject_has('project.name')"
```

---

## Variable Resolution

Variables are resolved in priority order (highest first):

1. **CLI arguments**: `--var name=value`
2. **Environment variables**: `ADT_VAR_NAME`
3. **Profile variables**: From `profile.toml` `[variables]`
4. **Extended profile variables**: From parent profiles
5. **Project pyproject.toml**: Values from `[project]` and `[tool.adt]`
6. **Global config variables**: From `~/.config/adt/config.toml`
7. **Computed values**: Auto-detected from project context

### Computed Variables (Auto-detected)

| Variable | Source |
|----------|--------|
| `project_name` | Directory name or `pyproject.toml:[project].name` |
| `project_version` | `pyproject.toml:[project].version` or `"0.1.0"` |
| `project_description` | `pyproject.toml:[project].description` |
| `has_src_layout` | `True` if `src/` directory exists |
| `has_tests` | `True` if `tests/` directory exists |
| `current_year` | Current year (for copyright notices) |
| `python_version` | From `.python-version` or pyproject.toml |

### Template Context

Templates receive a context object with:

```python
{
    # All resolved variables
    "project_name": "my-project",
    "author": "John Doe",
    ...

    # Special objects
    "project": {  # From pyproject.toml
        "name": "my-project",
        "version": "0.1.0",
        ...
    },
    "env": {  # Environment variables
        "HOME": "/home/user",
        ...
    },
    "adt": {  # ADT metadata
        "version": "0.9.0",
        "profile": "python",
    },
}
```

---

## CLI Interface

### Basic Commands

```bash
# Seed with default profile
adt seed

# Seed with specific profile
adt seed --profile python
adt seed -p python

# Layer multiple profiles (applied in order)
adt seed -p python,web,docker

# Use a one-off source (no profile config needed)
adt seed --source ~/my-templates
adt seed --source git@github.com:user/templates.git
adt seed --source https://github.com/user/templates.git#branch:subdir
```

### Variables

```bash
# Set variables via CLI
adt seed --var author="John Doe" --var license=MIT

# Short form
adt seed -v author="John Doe" -v license=MIT

# Interactive mode - prompt for missing required variables
adt seed --interactive
adt seed -i
```

### File Handling

```bash
# Default: skip existing files
adt seed

# Overwrite existing files (with confirmation)
adt seed --overwrite

# Overwrite without confirmation
adt seed --overwrite --yes

# Dry run - show what would be created/modified
adt seed --dry-run

# Show diff of what would change
adt seed --diff
```

### Script Control

```bash
# Skip running scripts
adt seed --no-scripts

# Run only scripts (no file operations)
adt seed --scripts-only

# List scripts that would run
adt seed --list-scripts
```

### Profile Management

```bash
# List available profiles
adt seed --list

# Show profile details
adt seed --info python

# Show resolved variables for a profile
adt seed --show-vars -p python

# Validate a profile
adt seed --validate -p python
```

### Full Example

```bash
# Complex invocation
adt seed \
  --profile python \
  --profile web \
  --var author="Jane Smith" \
  --var use_docker=true \
  --overwrite \
  --dry-run
```

---

## Template System

### Jinja2 Templates

Files ending in `.j2` are processed as Jinja2 templates:

```
templates/
├── ruff.toml              # Copied as-is
├── Makefile.j2            # Rendered, saved as "Makefile"
└── pyproject.partial.toml.j2  # Rendered, saved as "pyproject.partial.toml"
```

### Template Example (`Makefile.j2`)

```makefile
# {{ project_name }} Makefile
# Generated by ADT Seed ({{ adt.profile }} profile)

.PHONY: all test lint format typecheck

all: lint typecheck test

test:
	uv run pytest{% if has_tests %} tests/{% endif %}

lint:
	adt check {% if has_src_layout %}src{% else %}{{ project_name }}{% endif %}

format:
	adt format

typecheck:
	adt typecheck {% if has_src_layout %}src{% else %}{{ project_name }}{% endif %}

{% if use_docker %}
docker-build:
	docker build -t {{ project_name }}:{{ project_version }} .
{% endif %}
```

### Custom Jinja2 Filters

ADT provides custom filters:

```jinja2
{{ "my-project" | snake_case }}     → my_project
{{ "my_project" | kebab_case }}     → my-project
{{ "my project" | pascal_case }}    → MyProject
{{ items | to_toml }}               → TOML-formatted output
{{ data | to_yaml }}                → YAML-formatted output
{{ path | path_exists }}            → True/False
```

### Custom Jinja2 Functions

```jinja2
{% if path_exists('src/') %}
src_layout = true
{% endif %}

{% if pyproject_get('project.name') %}
name = "{{ pyproject_get('project.name') }}"
{% endif %}

{{ include_if('optional-section.toml.j2', use_feature) }}
```

---

## Scripts

### Script Execution

Scripts in `scripts/` are executed in alphabetical order after files are seeded:

```
scripts/
├── 01-install-deps.sh      # Runs first
├── 02-setup-hooks.sh       # Runs second
└── 03-init-git.sh          # Runs third
```

### Script Environment

Scripts receive environment variables:

```bash
# Project info
ADT_PROJECT_DIR=/path/to/project
ADT_PROJECT_NAME=my-project

# Profile info
ADT_PROFILE=python
ADT_PROFILE_DIR=/path/to/profile

# All template variables as ADT_VAR_*
ADT_VAR_AUTHOR="John Doe"
ADT_VAR_PYTHON_VERSION="3.12"
```

### Script Example (`01-install-deps.sh`)

```bash
#!/bin/bash
set -e

echo "Installing development dependencies..."

# Only run if uv.lock doesn't exist or --force
if [[ ! -f "uv.lock" ]] || [[ "$ADT_FORCE" == "true" ]]; then
    uv add --dev ruff ty pytest pytest-cov
fi

# Install pre-commit hooks if config exists
if [[ -f ".pre-commit-config.yaml" ]]; then
    uv run pre-commit install
fi
```

### Script Conditions

Scripts can check conditions before running:

```toml
# profile.toml
[scripts]
post_seed = [
    { script = "scripts/install-deps.sh", condition = "not path_exists('uv.lock')" },
    { script = "scripts/setup-hooks.sh", condition = "path_exists('.pre-commit-config.yaml')" },
]
```

---

## Profile Layering

Profiles can extend other profiles, creating a composition chain:

```
base → python → web → my-project
```

### Resolution Order

1. Load base profile
2. Load each extended profile in order
3. Merge configurations:
   - **Variables**: Later profiles override earlier ones
   - **Files**: Later profiles add to or override file mappings
   - **Scripts**: Concatenated in profile order

### Example: Layered Profiles

**base/profile.toml**:
```toml
[profile]
name = "base"

[variables]
author = "Unknown"
license = "MIT"
```

**python/profile.toml**:
```toml
[profile]
name = "python"
extends = ["base"]

[variables]
python_version = "3.12"
use_ruff = true
```

**web/profile.toml**:
```toml
[profile]
name = "web"
extends = ["python"]

[variables]
use_docker = true
web_framework = "litestar"
```

Seeding with `-p web` resolves variables as:
```python
{
    "author": "Unknown",        # from base
    "license": "MIT",           # from base
    "python_version": "3.12",   # from python
    "use_ruff": True,           # from python
    "use_docker": True,         # from web
    "web_framework": "litestar" # from web
}
```

---

## Diff and Update Mode (for `adt cruft`)

### Show Differences

```bash
# Show what's different between current files and profile templates
adt cruft --diff
adt cruft --diff --profile web

# Output format options
adt cruft --diff --format unified   # Default: unified diff
adt cruft --diff --format side      # Side-by-side
adt cruft --diff --format summary   # Just file names and status
```

### Diff Output Example

```
$ adt cruft --diff --profile python

Comparing against profile: python

Modified files:
  M ruff.toml
    - line-length = 88
    + line-length = 100

  M Makefile
    @@ -10,6 +10,9 @@
     test:
         uv run pytest
    +
    +coverage:
    +    uv run pytest --cov

Missing files (would be created):
  + .pre-commit-config.yaml
  + .github/workflows/ci.yml

Extra files (not in profile):
  ? custom-config.toml

Up to date:
  = .gitignore
  = pyproject.toml
```

---

## Git Repository Sources

### URL Formats

```toml
[sources]
# SSH
company = "git@github.com:company/adt-profiles.git"

# HTTPS
public = "https://github.com/user/adt-profiles.git"

# With branch/tag
versioned = "git@github.com:company/profiles.git#v2.0"

# With subdirectory
mono = "git@github.com:company/monorepo.git#main:tools/adt-profiles"

# Full format
full = "git@github.com:company/repo.git#branch:path/to/profiles"
```

### Caching

Remote profiles are cached locally:

```
~/.cache/adt/profiles/
├── github.com/
│   └── company/
│       └── adt-profiles/
│           ├── .git/
│           └── python/
│               └── profile.toml
```

### Update Cached Profiles

```bash
# Update all cached profiles
adt seed --update-cache

# Update specific profile
adt seed --update-cache --profile company

# Force fresh clone
adt seed --no-cache --profile company
```

---

## Project-Level Configuration

Projects can specify ADT seed preferences in `pyproject.toml`:

```toml
[tool.adt]
# Default profile for this project
profile = "python"

# Additional profiles to layer
profiles = ["python", "cli"]

# Project-specific variable overrides
[tool.adt.variables]
use_docker = false
ci_provider = "github"

# Ignore certain files from seeding
[tool.adt.seed]
ignore = [
    "Makefile",      # I have a custom one
    ".github/*",     # Managing CI separately
]
```

---

## Implementation Phases

### Phase 1: Core Infrastructure
- [ ] Config file loading (`~/.config/adt/config.toml`)
- [ ] Profile discovery and loading (local paths)
- [ ] Basic profile structure validation
- [ ] Variable resolution system

### Phase 2: Template Processing
- [ ] Jinja2 environment setup with custom filters
- [ ] Variable collection from all sources
- [ ] Template rendering with `.j2` detection
- [ ] File writing with directory creation

### Phase 3: Profile Layering
- [ ] Profile inheritance resolution
- [ ] Variable merging
- [ ] File mapping merging
- [ ] Circular dependency detection

### Phase 4: File Operations
- [ ] Skip existing files (default)
- [ ] `--overwrite` with confirmation
- [ ] `--dry-run` mode
- [ ] `--diff` output

### Phase 5: Script Execution
- [ ] Script discovery in profiles
- [ ] Environment variable setup
- [ ] Safe execution with output capture
- [ ] Conditional script execution

### Phase 6: Git Repository Support
- [ ] URL parsing (SSH, HTTPS, branch, subdir)
- [ ] Clone/fetch operations
- [ ] Local caching
- [ ] Cache invalidation and updates

### Phase 7: Enhanced UX
- [ ] Interactive mode (`--interactive`)
- [ ] `--list` and `--info` commands
- [ ] Progress output and logging
- [ ] Error messages with suggestions

### Phase 8: Cruft Diff Integration
- [ ] Diff generation against profile
- [ ] Multiple output formats
- [ ] Integration with `adt cruft` command

---

## Example Profiles

### Minimal Python Profile

```
python-minimal/
├── profile.toml
└── templates/
    ├── ruff.toml
    ├── .gitignore
    └── Makefile.j2
```

**profile.toml**:
```toml
[profile]
name = "python-minimal"
description = "Minimal Python setup with ruff"

[variables]
python_version = "3.12"
```

### Full Python Profile

```
python-full/
├── profile.toml
├── templates/
│   ├── ruff.toml
│   ├── .gitignore
│   ├── Makefile.j2
│   ├── .pre-commit-config.yaml.j2
│   ├── noxfile.py.j2
│   └── .github/
│       └── workflows/
│           └── ci.yml.j2
└── scripts/
    ├── 01-install-deps.sh
    └── 02-setup-pre-commit.sh
```

---

## Open Questions

1. **Merge vs Replace for existing files?**
   - Should `--overwrite` completely replace, or try to merge (e.g., TOML sections)?
   - Initial answer: Replace only, merging is too complex and error-prone

2. **Template language alternatives?**
   - Jinja2 is standard but heavy
   - Consider simpler `${var}` syntax for non-.j2 files?
   - Initial answer: Jinja2 only, keep it simple

3. **Profile versioning?**
   - Should profiles declare compatibility with ADT versions?
   - Should there be a profile schema version?
   - Initial answer: Add `adt_version` field, warn on mismatch

4. **Conflict resolution in layering?**
   - What if two profiles define the same file differently?
   - Initial answer: Last profile wins, warn user

5. **Security for remote profiles?**
   - Scripts from remote repos could be malicious
   - Initial answer: `confirm_scripts = true` by default, show script content before running

---

## Success Criteria

1. **Zero-config works**: `adt seed` with no arguments seeds sensible defaults
2. **Personal profiles**: Users can maintain their own profile collections
3. **Composable**: Layer profiles without conflicts
4. **Transparent**: Clear what will happen before it happens (dry-run, diff)
5. **Safe**: Never lose user data without explicit consent
6. **Fast**: Profile resolution and templating should be instant
7. **Debuggable**: Easy to understand why a variable has a certain value

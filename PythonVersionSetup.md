# Semantic Release: Complete Guide for Python Monorepo

## What is Semantic Release?

Semantic Release is an automated versioning and publishing system that removes the manual work of deciding version numbers, creating releases, and publishing packages. Instead of developers manually updating version files, it uses **commit messages** to automatically determine what type of version bump is needed.

## How Semantic Versioning Works

Semantic versioning follows the format: **MAJOR.MINOR.PATCH** (e.g., 2.1.3)

- **MAJOR** (2.0.0): Breaking changes that aren't backward compatible
- **MINOR** (1.1.0): New features that are backward compatible  
- **PATCH** (1.0.1): Bug fixes that are backward compatible

## How Semantic Release Determines Versions

Semantic Release analyzes your **commit messages** since the last release to automatically decide the version bump:

### Commit Message Format → Version Impact

```bash
# PATCH version bump (1.0.0 → 1.0.1)
fix: resolve login timeout issue
fix: handle edge case in user validation

# MINOR version bump (1.0.0 → 1.1.0)  
feat: add user profile management
feat: implement password reset functionality

# MAJOR version bump (1.0.0 → 2.0.0)
feat: redesign authentication system

BREAKING CHANGE: API endpoints now require JWT tokens instead of API keys
```

### Multiple Commits in One Release

If you have multiple commits since the last release, Semantic Release takes the **highest** level change:

```bash
git commit -m "docs: update README"        # No version bump
git commit -m "fix: resolve login bug"     # PATCH bump  
git commit -m "feat: add user dashboard"   # MINOR bump
# Result: MINOR version bump (because feat > fix > docs)
```

## The Complete Workflow

### 1. **Developer Commits** (Manual)
```bash
# Developer works on features
git add .
git commit -m "feat: add user authentication"
git push origin feature-branch
```

### 2. **Merge to Main** (Manual)
```bash
# PR/MR gets merged to main branch
git checkout main
git merge feature-branch
```

### 3. **Automatic Release** (Semantic Release)
When code is pushed to main, Semantic Release:

1. **Analyzes commits** since last release
2. **Calculates new version** based on commit types
3. **Updates version** in pyproject.toml
4. **Generates changelog** from commit messages
5. **Creates git tag** (e.g., v1.2.0)
6. **Builds package** using `uv build`
7. **Publishes to artifactory** automatically
8. **Creates release** in GitLab with changelog

### Example Flow in Your Monorepo

```bash
# Current state: project-a is at v1.0.0

# Developer commits
git commit -m "feat: add user login"      # Will trigger MINOR bump
git commit -m "fix: handle timeout"      # Will trigger PATCH bump  
git commit -m "docs: update API docs"    # No version bump

# When merged to main, Semantic Release sees all commits:
# - feat: → MINOR bump needed
# - fix: → PATCH bump needed  
# - docs: → no bump needed
# Result: MINOR bump (feat wins) → v1.1.0

# Automatic actions:
# ✅ Version updated: 1.0.0 → 1.1.0
# ✅ Git tag created: v1.1.0  
# ✅ Package built and published to artifactory
# ✅ Changelog updated with new features and fixes
# ✅ GitLab release created
```

## Benefits for Your Team

### Before Semantic Release:
```bash
# Manual process (error-prone)
1. Developer: "What version should this be?"
2. Developer: Manually edit version file
3. Developer: Remember to update changelog
4. Developer: Create git tag manually
5. CI: Build and publish
6. Often forgotten or done inconsistently
```

### After Semantic Release:
```bash
# Automated process (consistent)
1. Developer: Write descriptive commit message
2. Merge to main
3. Everything else happens automatically
4. Perfect consistency across all projects
```

### Key Advantages:

- **No version conflicts**: No merge conflicts on version files
- **Consistent versioning**: Same rules applied across all projects
- **Better documentation**: Auto-generated changelogs from commits
- **Faster releases**: No manual release process
- **Clear history**: Git tags and releases automatically created
- **Enforced standards**: Encourages good commit message practices

## Your Monorepo Setup

In your monorepo with multiple Python projects:

```
monorepo/
├── project-a/          # Independent versioning
│   ├── pyproject.toml  # version: 1.2.3
│   └── src/
├── project-b/          # Independent versioning  
│   ├── pyproject.toml  # version: 2.0.1
│   └── src/
└── .gitlab-ci.yml      # Detects which projects changed
```

**Independent Versioning**: Each project gets its own version based on its own changes:
- Changes to `project-a/` → only `project-a` gets new version
- Changes to `project-b/` → only `project-b` gets new version
- Changes to both → both get new versions

## The Human-Friendly Approach

We'll set up the system so your team can adopt it gradually:

1. **Immediate benefit**: Works even with non-conventional commits
2. **Helpful warnings**: Lefthook suggests better commit messages (doesn't block)
3. **Easy fixes**: Simple commands to amend commit messages
4. **Guided mode**: Commitizen for interactive conventional commits
5. **No disruption**: All existing workflows continue to work

---

## Complete Setup: Python Semantic Release + Lefthook + Commitizen (GitLab)

### 1. **Python Semantic Release** (Core Automation)

**Installation & Configuration:**
```bash
uv add --dev python-semantic-release
```

```toml
# pyproject.toml
[tool.semantic_release]
version_toml = ["pyproject.toml:project.version"]
branch = "main"
upload_to_pypi = false
upload_to_repository = true
repository_url = "https://your-artifactory.com/pypi/"
changelog_file = "CHANGELOG.md"
build_command = "uv build"
vcs_release = true
```

**GitLab CI Pipeline:**
```yaml
# .gitlab-ci.yml
stages:
  - test
  - release

variables:
  PIP_CACHE_DIR: "$CI_PROJECT_DIR/.cache/pip"

cache:
  paths:
    - .cache/pip
    - .venv/

before_script:
  - python -m pip install --upgrade pip
  - pip install uv
  - uv sync --dev

test:
  stage: test
  script:
    - uv run pytest
  only:
    - merge_requests
    - main

release:
  stage: release
  script:
    - git config user.name "gitlab-ci-token"
    - git config user.email "gitlab-ci-token@gitlab.example.com"
    - uv run semantic-release publish
  only:
    - main
  variables:
    GL_TOKEN: $CI_JOB_TOKEN
    REPOSITORY_USERNAME: gitlab-ci-token
    REPOSITORY_PASSWORD: $CI_JOB_TOKEN
  # For artifactory authentication
  before_script:
    - python -m pip install --upgrade pip
    - pip install uv
    - uv sync --dev
    - echo "Setting up artifactory credentials..."
```

### 2. **Lefthook Configuration** (Unblocking Warnings)

**Lefthook Setup:**
```yaml
# lefthook.yml
commit-msg:
  commands:
    commit-helper:
      run: python scripts/commit_helper.py {1}
      fail_text: "Commit message helper failed"
      skip:
        - merge
        - rebase

pre-push:
  commands:
    tests:
      run: uv run pytest --fast
      fail_text: "Tests failed"
```

**Warning Script:**
```python
# scripts/commit_helper.py
#!/usr/bin/env python3
import sys
import re
import os

def main():
    if len(sys.argv) < 2:
        return 0
    
    commit_msg_file = sys.argv[1]
    
    # Skip if file doesn't exist (can happen during rebases)
    if not os.path.exists(commit_msg_file):
        return 0
    
    with open(commit_msg_file, 'r') as f:
        commit_msg = f.read().strip()
    
    # Skip empty commits or merge commits
    if not commit_msg or commit_msg.startswith('Merge'):
        return 0
    
    first_line = commit_msg.split('\n')[0]
    
    # Check conventional format
    conventional_pattern = r'^(feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert)(\(.+\))?: .+'
    
    if not re.match(conventional_pattern, first_line):
        print("\n⚠️  HEADS UP: This commit won't trigger an automatic release!")
        print(f"   Current: '{first_line}'")
        print("\n🚀 For automatic versioning, use these formats:")
        print(f"   feat: {first_line}  (new feature → minor version)")
        print(f"   fix: {first_line}   (bug fix → patch version)")
        print(f"   docs: {first_line}  (documentation only)")
        print("\n🛠️  Quick fixes:")
        print(f"   git commit --amend -m 'feat: {first_line}'")
        print(f"   git commit --amend -m 'fix: {first_line}'")
        print("\n💡 Or use guided commits next time: uv run cz commit")
        print("✅ Proceeding with commit anyway...\n")
    
    return 0  # Always allow commit

if __name__ == "__main__":
    sys.exit(main())
```

### 3. **Commitizen** (Interactive Tool)

**Installation & Setup:**
```bash
uv add --dev commitizen
```

```toml
# pyproject.toml (add to existing config)
[tool.commitizen]
name = "cz_conventional_commits"
tag_format = "v$version"
version_scheme = "semver"
version_provider = "pep621"
update_changelog_on_bump = true
```

### 4. **GitLab-Specific Configuration**

**Enhanced GitLab CI for Monorepo:**
```yaml
# .gitlab-ci.yml
include:
  - template: Security/SAST.gitlab-ci.yml

stages:
  - test
  - release

variables:
  PIP_CACHE_DIR: "$CI_PROJECT_DIR/.cache/pip"
  FF_USE_FASTZIP: "true"
  CACHE_COMPRESSION_LEVEL: "fastest"

.uv_template: &uv_setup
  before_script:
    - python -m pip install --upgrade pip
    - pip install uv
    - uv sync --dev

# Detect which projects changed
detect-changes:
  stage: test
  image: alpine/git
  script:
    - |
      if [ "$CI_COMMIT_BEFORE_SHA" = "0000000000000000000000000000000000000000" ]; then
        echo "Initial commit, releasing all projects"
        echo "project-a=true" > changes.env
        echo "project-b=true" >> changes.env
      else
        git diff --name-only $CI_COMMIT_BEFORE_SHA $CI_COMMIT_SHA > changed_files.txt
        if grep -q "^project-a/" changed_files.txt; then
          echo "project-a=true" > changes.env
        else
          echo "project-a=false" > changes.env
        fi
        if grep -q "^project-b/" changed_files.txt; then
          echo "project-b=true" >> changes.env
        else
          echo "project-b=false" >> changes.env
        fi
      fi
  artifacts:
    reports:
      dotenv: changes.env
  only:
    - main

# Release project A
release-project-a:
  <<: *uv_setup
  stage: release
  script:
    - cd project-a
    - git config user.name "gitlab-ci-token"
    - git config user.email "gitlab-ci-token@gitlab.example.com"
    - uv run semantic-release publish
  only:
    variables:
      - $project_a == "true"
    refs:
      - main
  variables:
    GL_TOKEN: $CI_JOB_TOKEN
  dependencies:
    - detect-changes

# Release project B  
release-project-b:
  <<: *uv_setup
  stage: release
  script:
    - cd project-b
    - git config user.name "gitlab-ci-token" 
    - git config user.email "gitlab-ci-token@gitlab.example.com"
    - uv run semantic-release publish
  only:
    variables:
      - $project_b == "true"
    refs:
      - main
  variables:
    GL_TOKEN: $CI_JOB_TOKEN
  dependencies:
    - detect-changes
```

### 5. **Lefthook Installation & Git Aliases**

**Installation Script:**
```bash
#!/bin/bash
# setup-lefthook-semantic.sh

echo "🚀 Setting up Semantic Release with Lefthook..."

# Install lefthook (if not already installed)
if ! command -v lefthook &> /dev/null; then
    echo "Installing lefthook..."
    # For macOS
    brew install lefthook
    # For Linux (or use package manager)
    # curl -1sLf 'https://dl.cloudsmith.io/public/evilmartians/lefthook/setup.deb.sh' | sudo -E bash
    # sudo apt install lefthook
fi

# Install Python dependencies
uv add --dev python-semantic-release commitizen

# Create scripts directory
mkdir -p scripts

# Install lefthook hooks
lefthook install

# Set up git aliases
git config alias.cz '!uv run cz commit'
git config alias.feat '!f() { git commit -m "feat: $*"; }; f'
git config alias.fix '!f() { git commit -m "fix: $*"; }; f'
git config alias.docs '!f() { git commit -m "docs: $*"; }; f'
git config alias.chore '!f() { git commit -m "chore: $*"; }; f'

echo "✅ Setup complete!"
echo ""
echo "📋 Usage:"
echo "  Guided commit:     uv run cz commit"
echo "  Quick feat:        git feat 'add new feature'"
echo "  Quick fix:         git fix 'resolve bug'"
echo "  Normal commit:     git commit -m 'your message' (gets helpful warning)"
echo "  Skip hooks:        git commit --no-verify -m 'emergency fix'"
```

### 6. **GitLab CI Variables Setup**

**Required GitLab CI/CD Variables:**
```bash
# In GitLab Project Settings > CI/CD > Variables

# For Artifactory (if using)
ARTIFACTORY_URL=https://your-artifactory.com/pypi/
ARTIFACTORY_USERNAME=your-username
ARTIFACTORY_PASSWORD=your-token

# For GitLab releases (automatic)
GL_TOKEN=$CI_JOB_TOKEN  # This is automatic in GitLab

# For custom registry authentication
REPOSITORY_USERNAME=gitlab-ci-token
REPOSITORY_PASSWORD=$CI_JOB_TOKEN
```

### 7. **Advanced Lefthook Configuration**

**Extended Lefthook with More Hooks:**
```yaml
# lefthook.yml
pre-commit:
  commands:
    lint:
      glob: "*.py"
      run: uv run ruff check {staged_files}
      stage_fixed: true
    format:
      glob: "*.py" 
      run: uv run ruff format {staged_files}
      stage_fixed: true

commit-msg:
  commands:
    commit-helper:
      run: python scripts/commit_helper.py {1}
      fail_text: "Commit message helper failed"
      skip:
        - merge
        - rebase

pre-push:
  commands:
    tests:
      run: uv run pytest --fast
      fail_text: "Tests failed"
    semantic-check:
      run: python scripts/check_semantic_readiness.py
      fail_text: "Semantic release check failed"

# Skip hooks for emergency commits
skip_output:
  - meta
  - execution
```

### 8. **Team Workflow Summary**

**Developer Workflow:**
1. **Regular development**: `git feat "add user auth"` → Lefthook warns if needed
2. **Guided commits**: `uv run cz commit` → Interactive conventional commits  
3. **Emergency bypass**: `git commit --no-verify -m "hotfix"` → Skip all hooks
4. **Fix warnings**: `git commit --amend -m "feat: add user auth"`

**CI/CD Flow:**
1. **Push to MR**: Runs tests only
2. **Merge to main**: 
   - Detects changed projects
   - Runs semantic-release for each changed project
   - Automatically versions, tags, and publishes to artifactory
   - Creates GitLab releases with auto-generated changelogs

**Benefits over Pre-commit:**
- ⚡ **Faster**: Lefthook is written in Go, much faster than pre-commit
- 🔧 **More flexible**: Better skip mechanisms and conditional execution  
- 📦 **Single binary**: No Python dependency for the hook runner
- 🎯 **GitLab native**: Better integration with GitLab CI/CD

This setup gives you the same semantic release automation with the performance and flexibility benefits of Lefthook in a GitLab environment.

Here's the complete setup adapted for GitLab CI and Lefthook:

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

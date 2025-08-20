#!/usr/bin/env python3
"""
Commit message helper for monorepo
Provides warnings and suggestions for better conventional commits
"""
import sys
import re
import os

def get_available_projects():
    """Get list of available projects in packages/ and libs/"""
    projects = []
    
    for search_dir in ['packages', 'libs']:
        if not os.path.exists(search_dir):
            continue
        for item in os.listdir(search_dir):
            project_path = os.path.join(search_dir, item)
            if os.path.isdir(project_path) and not item.startswith('.'):
                if os.path.exists(os.path.join(project_path, 'pyproject.toml')):
                    projects.append(item)
    
    return sorted(projects)

def analyze_commit_message(commit_msg):
    """Analyze commit message and provide feedback"""
    first_line = commit_msg.split('\n')[0]
    
    # Check for conventional format
    conventional_pattern = r'^(feat|fix|docs|style|refactor|perf|test|build|ci|chore)(\([^)]+\))?: .+'
    scoped_pattern = r'^(feat|fix|docs|style|refactor|perf|test|build|ci|chore)\([^)]+\): .+'
    
    is_conventional = bool(re.match(conventional_pattern, first_line))
    is_scoped = bool(re.match(scoped_pattern, first_line))
    
    return {
        'is_conventional': is_conventional,
        'is_scoped': is_scoped,
        'first_line': first_line
    }

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
    
    analysis = analyze_commit_message(commit_msg)
    projects = get_available_projects()
    
    if not analysis['is_conventional']:
        print("\n⚠️  HEADS UP: This commit won't trigger automatic releases!")
        print(f"   Current: '{analysis['first_line']}'")
        print("\n🚀 For automatic versioning, use conventional commit format:")
        print(f"   feat: {analysis['first_line']}   (new feature → minor version)")
        print(f"   fix: {analysis['first_line']}    (bug fix → patch version)")
        print(f"   docs: {analysis['first_line']}   (documentation only)")
        print("\n📦 For project-specific releases, use scopes:")
        
        # Show first few projects as examples
        example_projects = projects[:3] if projects else ['user-service', 'auth-utils']
        for project in example_projects:
            print(f"   feat({project}): {analysis['first_line']}")
        
        if len(projects) > 3:
            print(f"   ... (and {len(projects) - 3} more projects)")
        
        print(f"\n📋 Available projects: {', '.join(projects[:8])}")
        if len(projects) > 8:
            print(f"    ... and {len(projects) - 8} more")
        
        print("\n🛠️  Quick fixes:")
        print(f"   git commit --amend -m 'feat: {analysis['first_line']}'")
        print(f"   git commit --amend -m 'fix: {analysis['first_line']}'")
        print("\n💡 Or use guided commits: uv run cz commit")
        print("✅ Proceeding with commit anyway...\n")
    
    elif analysis['is_conventional'] and not analysis['is_scoped']:
        print(f"\n✅ Good conventional commit!")
        print(f"   This will trigger releases for all changed projects")
        print(f"   Tip: Use scopes like 'feat(project-name):' for more precise control\n")
    
    return 0  # Always allow commit

if __name__ == "__main__":
    sys.exit(main())
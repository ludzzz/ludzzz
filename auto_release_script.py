#!/usr/bin/env python3
"""
Automatic release script for Python monorepo
Analyzes commits, determines version bumps, and releases changed projects
"""
import os
import subprocess
import toml
from packaging import version
import re
import sys

def get_projects_to_release():
    """Find projects that have changes since their last release"""
    projects_to_release = []
    
    for folder in ['packages', 'libs']:
        if not os.path.exists(folder):
            print(f"Warning: {folder}/ directory not found")
            continue
            
        for project_dir in os.listdir(folder):
            project_path = f"{folder}/{project_dir}"
            
            # Skip if not a directory
            if not os.path.isdir(project_path):
                continue
                
            # Skip hidden directories
            if project_dir.startswith('.'):
                continue
                
            # Must have pyproject.toml
            if not os.path.exists(f"{project_path}/pyproject.toml"):
                continue
                
            print(f"🔍 Checking {project_path}...")
            
            # Check if project has changes since last tag
            last_tag = get_last_tag(project_dir)
            commits_since = get_commits_since_tag(project_path, last_tag)
            
            if commits_since:
                bump_type = analyze_commits(commits_since, project_dir)
                if bump_type:
                    projects_to_release.append({
                        'name': project_dir,
                        'path': project_path,
                        'folder': folder,
                        'bump_type': bump_type,
                        'commits': len(commits_since),
                        'last_tag': last_tag
                    })
                    print(f"   ✅ Will release ({bump_type} bump, {len(commits_since)} commits)")
                else:
                    print(f"   ⏭️  Has commits but no version-bumping changes")
            else:
                print(f"   ⏭️  No changes since last release")
    
    return projects_to_release

def get_last_tag(project_name):
    """Get the last version tag for a project"""
    try:
        cmd = ['git', 'tag', '-l', f'{project_name}-v*', '--sort=-version:refname']
        result = subprocess.run(cmd, capture_output=True, text=True)
        tags = [t for t in result.stdout.strip().split('\n') if t and t.strip()]
        return tags[0] if tags else None
    except Exception as e:
        print(f"   Warning: Could not get tags for {project_name}: {e}")
        return None

def get_commits_since_tag(project_path, last_tag):
    """Get commits affecting this project since last tag"""
    try:
        if last_tag:
            cmd = ['git', 'log', f'{last_tag}..HEAD', '--oneline', '--', project_path]
        else:
            # No previous tags, get all commits for this project
            cmd = ['git', 'log', '--oneline', '--', project_path]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        commits = [c for c in result.stdout.strip().split('\n') if c.strip()]
        return commits
    except Exception as e:
        print(f"   Warning: Could not get commits for {project_path}: {e}")
        return []

def analyze_commits(commits, project_name):
    """Determine version bump type from commits"""
    relevant_commits = []
    
    # Filter commits that are relevant to this project
    for commit in commits:
        commit_msg = commit.split(' ', 1)[1] if ' ' in commit else commit
        
        # Include commits that:
        # 1. Are scoped to this project: feat(project-name): ...
        # 2. Are unscoped (affect the project directory): feat: ...
        if f'({project_name})' in commit_msg or not re.search(r'\([^)]+\):', commit_msg):
            relevant_commits.append(commit_msg)
    
    if not relevant_commits:
        return None
    
    print(f"   📝 Relevant commits:")
    for commit in relevant_commits[:3]:
        print(f"      - {commit}")
    if len(relevant_commits) > 3:
        print(f"      ... and {len(relevant_commits) - 3} more")
    
    # Analyze commit types
    has_breaking = any('BREAKING CHANGE' in c or 
                      '!' in c.split(':')[0] or
                      'BREAKING:' in c 
                      for c in relevant_commits)
    
    has_feat = any(c.strip().startswith('feat') for c in relevant_commits)
    has_fix = any(c.strip().startswith('fix') for c in relevant_commits)
    
    if has_breaking:
        return 'major'
    elif has_feat:
        return 'minor'
    elif has_fix:
        return 'patch'
    else:
        # Any other changes (docs, chore, etc.) get patch bump
        return 'patch'

def calculate_new_version(current_version, bump_type):
    """Calculate new version based on bump type"""
    current_ver = version.parse(current_version)
    
    if bump_type == 'major':
        return f"{current_ver.major + 1}.0.0"
    elif bump_type == 'minor':
        return f"{current_ver.major}.{current_ver.minor + 1}.0"
    else:  # patch
        return f"{current_ver.major}.{current_ver.minor}.{current_ver.micro + 1}"

def release_project(project):
    """Release a single project"""
    print(f"\n🚀 Releasing {project['name']} ({project['bump_type']} bump)")
    
    try:
        # Read current version from pyproject.toml
        with open(f"{project['path']}/pyproject.toml", 'r') as f:
            config = toml.load(f)
        
        current_version = config['project']['version']
        new_version = calculate_new_version(current_version, project['bump_type'])
        
        print(f"   📈 {current_version} → {new_version}")
        
        # Update version in pyproject.toml
        config['project']['version'] = new_version
        with open(f"{project['path']}/pyproject.toml", 'w') as f:
            toml.dump(config, f)
        
        print(f"   ✏️  Updated {project['path']}/pyproject.toml")
        
        # Commit the version change
        subprocess.run(['git', 'add', f"{project['path']}/pyproject.toml"], check=True)
        commit_msg = f"chore({project['name']}): release v{new_version}"
        subprocess.run(['git', 'commit', '-m', commit_msg], check=True)
        print(f"   ✅ Committed version update")
        
        # Build the package
        original_cwd = os.getcwd()
        os.chdir(project['path'])
        
        print(f"   🔨 Building package...")
        subprocess.run(['uv', 'build'], check=True)
        
        # Publish to repository
        print(f"   📦 Publishing to repository...")
        subprocess.run(['uv', 'publish'], check=True)
        
        os.chdir(original_cwd)
        
        # Create and push git tag
        tag_name = f"{project['name']}-v{new_version}"
        subprocess.run(['git', 'tag', tag_name], check=True)
        print(f"   🏷️  Created tag: {tag_name}")
        
        # Push version commit and tag
        subprocess.run(['git', 'push', 'origin', 'main'], check=True)
        subprocess.run(['git', 'push', 'origin', tag_name], check=True)
        print(f"   ⬆️  Pushed changes and tag")
        
        print(f"✅ Successfully released {project['name']} v{new_version}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to release {project['name']}: {e}")
        if 'original_cwd' in locals():
            os.chdir(original_cwd)
        return False

def main():
    """Main function - analyze and release all changed projects"""
    print("🔍 Analyzing monorepo for releases...")
    print("=" * 50)
    
    # Check if we're in a git repository
    try:
        subprocess.run(['git', 'rev-parse', '--git-dir'], 
                      capture_output=True, check=True)
    except subprocess.CalledProcessError:
        print("❌ Not in a git repository")
        return False
    
    # Find projects that need releasing
    projects = get_projects_to_release()
    
    if not projects:
        print("\n✅ No projects need releasing")
        return True
    
    print(f"\n📦 Found {len(projects)} projects to release:")
    print("=" * 50)
    
    for project in projects:
        last_version = "none" if not project['last_tag'] else project['last_tag'].split('-v')[1]
        print(f"  📦 {project['name']}")
        print(f"     Path: {project['path']}")
        print(f"     Last version: {last_version}")
        print(f"     Bump type: {project['bump_type']}")
        print(f"     Commits: {project['commits']}")
        print()
    
    print("🚀 Starting releases...")
    print("=" * 50)
    
    success_count = 0
    for project in projects:
        if release_project(project):
            success_count += 1
        else:
            print(f"⚠️  Continuing with remaining projects...")
    
    print("\n" + "=" * 50)
    print(f"📊 Release Summary:")
    print(f"   Total projects: {len(projects)}")
    print(f"   Successful: {success_count}")
    print(f"   Failed: {len(projects) - success_count}")
    
    if success_count == len(projects):
        print("🎉 All releases completed successfully!")
        return True
    else:
        print("⚠️  Some releases failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
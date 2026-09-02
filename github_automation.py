#!/usr/bin/env python3
"""
GitHub Automation Script for Claude Integration
Works with repositories at github.com/lukumaki/

Install dependencies:
  pip install PyGithub requests python-dotenv

Set up authentication:
  1. Create a .env file in the same directory
  2. Add: GITHUB_TOKEN=your_personal_access_token
  
  To generate a token:
  - Go to GitHub Settings > Developer settings > Personal access tokens
  - Create a token with 'repo', 'read:user', 'user:email' scopes
"""

import os
import json
from typing import Optional, List, Dict, Any
from datetime import datetime
from dotenv import load_dotenv
from github import Github, GithubException
import requests

# Load environment variables
load_dotenv()
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')

if not GITHUB_TOKEN:
    raise ValueError("GITHUB_TOKEN not found in environment. Please set it in .env file or environment.")

# Initialize GitHub client
gh = Github(GITHUB_TOKEN)
USER_LOGIN = 'lukumaki'


class GitHubAutomation:
    """Handle GitHub operations for lukumaki repositories"""
    
    def __init__(self, token: str, username: str = 'lukumaki'):
        self.gh = Github(token)
        self.user = self.gh.get_user(username)
        self.username = username
    
    # ===== REPOSITORY OPERATIONS =====
    
    def list_repos(self, include_stats: bool = True) -> List[Dict[str, Any]]:
        """List all repositories for the user"""
        repos = []
        try:
            for repo in self.user.get_repos(sort='updated', direction='desc'):
                repo_info = {
                    'name': repo.name,
                    'url': repo.html_url,
                    'description': repo.description,
                    'language': repo.language,
                    'stars': repo.stargazers_count,
                }
                if include_stats:
                    repo_info.update({
                        'forks': repo.forks_count,
                        'watchers': repo.watchers_count,
                        'open_issues': repo.open_issues_count,
                        'updated': repo.updated_at.isoformat() if repo.updated_at else None,
                    })
                repos.append(repo_info)
            return repos
        except GithubException as e:
            return {'error': f'Failed to list repositories: {str(e)}'}
    
    def get_repo_files(self, repo_name: str, path: str = '', file_types: Optional[List[str]] = None) -> Dict[str, Any]:
        """Get file structure and optionally filter by file type"""
        try:
            repo = self.user.get_repo(repo_name)
            contents = repo.get_contents(path)
            
            files = []
            for item in contents:
                if item.type == 'file':
                    # Filter by file type if specified
                    if file_types and not any(item.name.endswith(ft) for ft in file_types):
                        continue
                    files.append({
                        'name': item.name,
                        'path': item.path,
                        'size': item.size,
                        'url': item.html_url,
                    })
                elif item.type == 'dir':
                    files.append({
                        'name': item.name + '/',
                        'path': item.path,
                        'type': 'directory',
                    })
            return {
                'repo': repo_name,
                'path': path if path else 'root',
                'files': files
            }
        except GithubException as e:
            return {'error': f'Failed to get files: {str(e)}'}
    
    def read_file(self, repo_name: str, file_path: str) -> Dict[str, Any]:
        """Read contents of a specific file"""
        try:
            repo = self.user.get_repo(repo_name)
            content = repo.get_contents(file_path)
            
            if content.type != 'file':
                return {'error': f'{file_path} is not a file'}
            
            return {
                'repo': repo_name,
                'file': file_path,
                'size': content.size,
                'content': content.decoded_content.decode('utf-8'),
                'url': content.html_url,
            }
        except GithubException as e:
            return {'error': f'Failed to read file: {str(e)}'}
    
    # ===== ISSUE OPERATIONS =====
    
    def list_issues(self, repo_name: str, state: str = 'open') -> Dict[str, Any]:
        """List issues in a repository"""
        try:
            repo = self.user.get_repo(repo_name)
            issues = []
            for issue in repo.get_issues(state=state, sort='updated'):
                issues.append({
                    'number': issue.number,
                    'title': issue.title,
                    'state': issue.state,
                    'labels': [label.name for label in issue.labels],
                    'created': issue.created_at.isoformat(),
                    'updated': issue.updated_at.isoformat(),
                    'url': issue.html_url,
                })
            return {
                'repo': repo_name,
                'state': state,
                'issues': issues
            }
        except GithubException as e:
            return {'error': f'Failed to list issues: {str(e)}'}
    
    def create_issue(self, repo_name: str, title: str, body: str = '', 
                    labels: Optional[List[str]] = None) -> Dict[str, Any]:
        """Create a new issue"""
        try:
            repo = self.user.get_repo(repo_name)
            issue = repo.create_issue(title=title, body=body, labels=labels or [])
            return {
                'success': True,
                'issue': {
                    'number': issue.number,
                    'title': issue.title,
                    'url': issue.html_url,
                }
            }
        except GithubException as e:
            return {'error': f'Failed to create issue: {str(e)}'}
    
    # ===== PULL REQUEST OPERATIONS =====
    
    def list_pull_requests(self, repo_name: str, state: str = 'open') -> Dict[str, Any]:
        """List pull requests in a repository"""
        try:
            repo = self.user.get_repo(repo_name)
            prs = []
            for pr in repo.get_pulls(state=state, sort='updated'):
                prs.append({
                    'number': pr.number,
                    'title': pr.title,
                    'state': pr.state,
                    'author': pr.user.login,
                    'created': pr.created_at.isoformat(),
                    'updated': pr.updated_at.isoformat(),
                    'url': pr.html_url,
                })
            return {
                'repo': repo_name,
                'state': state,
                'pull_requests': prs
            }
        except GithubException as e:
            return {'error': f'Failed to list PRs: {str(e)}'}
    
    def get_pr_details(self, repo_name: str, pr_number: int) -> Dict[str, Any]:
        """Get detailed information about a pull request"""
        try:
            repo = self.user.get_repo(repo_name)
            pr = repo.get_pull(pr_number)
            return {
                'number': pr.number,
                'title': pr.title,
                'state': pr.state,
                'author': pr.user.login,
                'body': pr.body,
                'commits': pr.commits,
                'changed_files': pr.changed_files,
                'additions': pr.additions,
                'deletions': pr.deletions,
                'url': pr.html_url,
            }
        except GithubException as e:
            return {'error': f'Failed to get PR details: {str(e)}'}
    
    # ===== CODE ANALYSIS =====
    
    def analyze_repo_structure(self, repo_name: str) -> Dict[str, Any]:
        """Get overview of repository structure and stats"""
        try:
            repo = self.user.get_repo(repo_name)
            
            # Count files by type
            file_counts = {}
            try:
                contents = repo.get_contents('')
                for item in contents:
                    if item.type == 'file':
                        ext = os.path.splitext(item.name)[1] or 'no_extension'
                        file_counts[ext] = file_counts.get(ext, 0) + 1
            except:
                pass
            
            return {
                'repo': repo_name,
                'description': repo.description,
                'language': repo.language,
                'topics': repo.topics,
                'stars': repo.stargazers_count,
                'forks': repo.forks_count,
                'open_issues': repo.open_issues_count,
                'created': repo.created_at.isoformat(),
                'updated': repo.updated_at.isoformat(),
                'file_types': file_counts,
                'url': repo.html_url,
            }
        except GithubException as e:
            return {'error': f'Failed to analyze repo: {str(e)}'}
    
    # ===== HELPER METHOD =====
    
    def run_command(self, command: str, **kwargs) -> Dict[str, Any]:
        """Execute a command by name - useful for API calls"""
        commands = {
            'list_repos': lambda: self.list_repos(**kwargs),
            'get_repo_files': lambda: self.get_repo_files(**kwargs),
            'read_file': lambda: self.read_file(**kwargs),
            'list_issues': lambda: self.list_issues(**kwargs),
            'create_issue': lambda: self.create_issue(**kwargs),
            'list_prs': lambda: self.list_pull_requests(**kwargs),
            'get_pr_details': lambda: self.get_pr_details(**kwargs),
            'analyze_repo': lambda: self.analyze_repo_structure(**kwargs),
        }
        
        if command not in commands:
            return {'error': f'Unknown command: {command}. Available: {list(commands.keys())}'}
        
        return commands[command]()


# ===== MAIN / TEST =====

if __name__ == '__main__':
    automation = GitHubAutomation(GITHUB_TOKEN, USER_LOGIN)
    
    print("GitHub Automation Script Initialized")
    print(f"User: {USER_LOGIN}\n")
    
    # Example: List all repositories
    print("=== Your Repositories ===")
    repos = automation.list_repos()
    for repo in repos[:5]:  # Show first 5
        print(f"- {repo['name']}: {repo['stars']} ⭐")
    
    print(f"\nTotal repos: {len(repos)}\n")
    
    # Example: Analyze a repo (if you have any)
    if repos:
        print(f"=== Analyzing {repos[0]['name']} ===")
        analysis = automation.analyze_repo_structure(repos[0]['name'])
        print(json.dumps(analysis, indent=2))

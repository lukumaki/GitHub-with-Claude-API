# GitHub Automation Script - Setup & Claude Integration Guide

## Quick Setup

### 1. Generate a GitHub Personal Access Token

1. Go to [GitHub Settings → Developer settings → Personal access tokens](https://github.com/settings/tokens)
2. Click "Generate new token"
3. Give it a name like `Claude-Automation`
4. Select these scopes:
   - `repo` (full control of private repositories)
   - `read:user`
   - `user:email`
5. Click "Generate token" and **copy it immediately** (you won't see it again)

### 2. Set Up Environment

```bash
# Navigate to the script directory
cd /path/to/script/directory

# Create a .env file
cat > .env << EOF
GITHUB_TOKEN=your_token_here
EOF

# Install dependencies
pip install PyGithub python-dotenv requests
```

### 3. Test the Script Locally

```bash
python github_automation.py
```

You should see your repositories listed.

---

## Using with Claude (API Integration)

### Option A: Direct Claude Integration (Recommended)

Create a wrapper script that Claude can call:

```python
# claude_github_client.py
import json
from github_automation import GitHubAutomation
import os
from dotenv import load_dotenv

load_dotenv()

def handle_request(request: dict) -> str:
    """Handle requests from Claude's API"""
    automation = GitHubAutomation(os.getenv('GITHUB_TOKEN'), 'lukumaki')
    
    command = request.get('command')
    params = request.get('params', {})
    
    result = automation.run_command(command, **params)
    return json.dumps(result, indent=2, default=str)

# Example usage:
if __name__ == '__main__':
    # This is what Claude would send
    request = {
        'command': 'list_repos',
        'params': {'include_stats': True}
    }
    print(handle_request(request))
```

### Option B: Use Claude Code (Desktop App)

If you have Claude Code desktop app:

1. Open Claude Code
2. Load this script into the terminal
3. Ask Claude to use it:
   - "List my repos and their stats"
   - "Read the README.md from my [repo-name]"
   - "Create an issue in [repo-name]"

### Option C: Schedule as Automation

Use a task scheduler to run periodic reports:

```bash
# macOS/Linux: Add to crontab
0 9 * * 1 cd /path/to/script && python github_automation.py > weekly_report.txt

# Windows: Create a scheduled task
python C:\path\to\github_automation.py
```

---

## Available Commands

### List Operations
```python
automation.list_repos(include_stats=True)
automation.list_issues('repo_name', state='open')  # state: 'open', 'closed', 'all'
automation.list_pull_requests('repo_name', state='open')
```

### Read Operations
```python
automation.get_repo_files('repo_name', path='', file_types=['.py', '.md'])
automation.read_file('repo_name', 'path/to/file.py')
automation.analyze_repo_structure('repo_name')
automation.get_pr_details('repo_name', pr_number=5)
```

### Write Operations
```python
automation.create_issue(
    repo_name='repo_name',
    title='Bug: Something broken',
    body='Description here',
    labels=['bug', 'urgent']
)
```

### Generic Command Runner
```python
automation.run_command('list_repos', include_stats=True)
automation.run_command('read_file', repo_name='repo_name', file_path='README.md')
automation.run_command('create_issue', repo_name='repo_name', title='New issue')
```

---

## Example Use Cases

### Use Case 1: Analyze all your repos
```python
automation = GitHubAutomation(token, 'lukumaki')
repos = automation.list_repos()
for repo in repos:
    analysis = automation.analyze_repo_structure(repo['name'])
    print(f"{repo['name']}: {analysis['stars']} stars, {analysis['open_issues']} issues")
```

### Use Case 2: Review recent PRs
```python
for repo_name in ['repo1', 'repo2']:
    prs = automation.list_pull_requests(repo_name, state='open')
    for pr in prs['pull_requests']:
        print(f"[{repo_name}] PR #{pr['number']}: {pr['title']}")
```

### Use Case 3: Create issues from Claude
```python
# Claude can ask you for details, then:
automation.create_issue(
    repo_name='my-project',
    title=user_provided_title,
    body=user_provided_description,
    labels=user_provided_labels
)
```

---

## How to Ask Claude to Use This

Once you have Claude Code set up:

1. **"List my GitHub repositories"**
   - Claude runs: `automation.list_repos()`

2. **"Read the README from my [repo-name]"**
   - Claude runs: `automation.read_file('repo-name', 'README.md')`

3. **"Show me open issues in all my projects"**
   - Claude loops through repos and gets issues

4. **"Create a new issue: [title and description]"**
   - Claude creates it with appropriate details

---

## Troubleshooting

### "GitHub token not found"
- Ensure `.env` file exists with `GITHUB_TOKEN=xxx`
- Check token is valid at https://github.com/settings/tokens

### "Repository not found"
- Make sure repo name exactly matches GitHub (case-sensitive)
- Token must have access to the repo

### "Rate limit exceeded"
- GitHub allows 60 requests/hour for unauthenticated, 5000/hour for authenticated
- Wait an hour or use a different token

### "Permission denied"
- Regenerate token with additional scopes if needed
- Token needs: `repo`, `read:user` at minimum

---

## Security Notes

- Never commit `.env` file to GitHub
- Add `.env` to `.gitignore`
- Use separate tokens for different purposes (local dev, CI/CD, etc.)
- Rotate tokens regularly
- Delete unused tokens from GitHub settings

---

## Next Steps

1. Set up the token and `.env` file
2. Test with `python github_automation.py`
3. If using Claude Code: ask Claude to help with GitHub tasks
4. Customize the script for your specific needs


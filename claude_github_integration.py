#!/usr/bin/env python3
"""
Example: Using GitHub Automation Script with Claude API

This shows how to:
1. Set up a tool that Claude can call
2. Make Claude requests with the tool available
3. Process Claude's responses

Install: pip install anthropic PyGithub python-dotenv
"""

import json
import os
from dotenv import load_dotenv
import anthropic
from github_automation import GitHubAutomation

# Load environment variables
load_dotenv()

GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
CLAUDE_API_KEY = os.getenv('ANTHROPIC_API_KEY')  # Claude API key

if not GITHUB_TOKEN:
    raise ValueError("GITHUB_TOKEN not found in .env")
if not CLAUDE_API_KEY:
    raise ValueError("ANTHROPIC_API_KEY not found in .env")


# ===== TOOL DEFINITIONS FOR CLAUDE =====

tools = [
    {
        "name": "list_repos",
        "description": "List all repositories for lukumaki with statistics",
        "input_schema": {
            "type": "object",
            "properties": {
                "include_stats": {
                    "type": "boolean",
                    "description": "Include repository statistics (default: true)",
                    "default": True
                }
            },
            "required": []
        }
    },
    {
        "name": "get_repo_files",
        "description": "Get file structure of a repository",
        "input_schema": {
            "type": "object",
            "properties": {
                "repo_name": {
                    "type": "string",
                    "description": "Repository name (e.g., 'my-project')"
                },
                "path": {
                    "type": "string",
                    "description": "Path within repo (default: root)",
                    "default": ""
                },
                "file_types": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Filter by file extensions (e.g., ['.py', '.md'])",
                    "default": None
                }
            },
            "required": ["repo_name"]
        }
    },
    {
        "name": "read_file",
        "description": "Read the contents of a specific file",
        "input_schema": {
            "type": "object",
            "properties": {
                "repo_name": {
                    "type": "string",
                    "description": "Repository name"
                },
                "file_path": {
                    "type": "string",
                    "description": "Path to the file within the repo"
                }
            },
            "required": ["repo_name", "file_path"]
        }
    },
    {
        "name": "list_issues",
        "description": "List issues in a repository",
        "input_schema": {
            "type": "object",
            "properties": {
                "repo_name": {
                    "type": "string",
                    "description": "Repository name"
                },
                "state": {
                    "type": "string",
                    "enum": ["open", "closed", "all"],
                    "description": "Issue state filter (default: open)",
                    "default": "open"
                }
            },
            "required": ["repo_name"]
        }
    },
    {
        "name": "create_issue",
        "description": "Create a new issue in a repository",
        "input_schema": {
            "type": "object",
            "properties": {
                "repo_name": {
                    "type": "string",
                    "description": "Repository name"
                },
                "title": {
                    "type": "string",
                    "description": "Issue title"
                },
                "body": {
                    "type": "string",
                    "description": "Issue description",
                    "default": ""
                },
                "labels": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Labels to attach (e.g., ['bug', 'urgent'])",
                    "default": []
                }
            },
            "required": ["repo_name", "title"]
        }
    },
    {
        "name": "list_pull_requests",
        "description": "List pull requests in a repository",
        "input_schema": {
            "type": "object",
            "properties": {
                "repo_name": {
                    "type": "string",
                    "description": "Repository name"
                },
                "state": {
                    "type": "string",
                    "enum": ["open", "closed", "all"],
                    "description": "PR state filter (default: open)",
                    "default": "open"
                }
            },
            "required": ["repo_name"]
        }
    },
    {
        "name": "get_pr_details",
        "description": "Get detailed information about a pull request",
        "input_schema": {
            "type": "object",
            "properties": {
                "repo_name": {
                    "type": "string",
                    "description": "Repository name"
                },
                "pr_number": {
                    "type": "integer",
                    "description": "Pull request number"
                }
            },
            "required": ["repo_name", "pr_number"]
        }
    },
    {
        "name": "analyze_repo",
        "description": "Get overview of repository structure and statistics",
        "input_schema": {
            "type": "object",
            "properties": {
                "repo_name": {
                    "type": "string",
                    "description": "Repository name"
                }
            },
            "required": ["repo_name"]
        }
    }
]


# ===== TOOL HANDLER =====

def handle_tool_call(tool_name: str, tool_input: dict) -> str:
    """Execute a tool call and return the result"""
    automation = GitHubAutomation(GITHUB_TOKEN, 'lukumaki')
    
    try:
        if tool_name == "list_repos":
            result = automation.list_repos(
                include_stats=tool_input.get("include_stats", True)
            )
        elif tool_name == "get_repo_files":
            result = automation.get_repo_files(
                repo_name=tool_input["repo_name"],
                path=tool_input.get("path", ""),
                file_types=tool_input.get("file_types")
            )
        elif tool_name == "read_file":
            result = automation.read_file(
                repo_name=tool_input["repo_name"],
                file_path=tool_input["file_path"]
            )
        elif tool_name == "list_issues":
            result = automation.list_issues(
                repo_name=tool_input["repo_name"],
                state=tool_input.get("state", "open")
            )
        elif tool_name == "create_issue":
            result = automation.create_issue(
                repo_name=tool_input["repo_name"],
                title=tool_input["title"],
                body=tool_input.get("body", ""),
                labels=tool_input.get("labels", [])
            )
        elif tool_name == "list_pull_requests":
            result = automation.list_pull_requests(
                repo_name=tool_input["repo_name"],
                state=tool_input.get("state", "open")
            )
        elif tool_name == "get_pr_details":
            result = automation.get_pr_details(
                repo_name=tool_input["repo_name"],
                pr_number=tool_input["pr_number"]
            )
        elif tool_name == "analyze_repo":
            result = automation.analyze_repo_structure(
                repo_name=tool_input["repo_name"]
            )
        else:
            result = {"error": f"Unknown tool: {tool_name}"}
        
        return json.dumps(result, indent=2, default=str)
    
    except Exception as e:
        return json.dumps({"error": str(e)})


# ===== CLAUDE INTEGRATION =====

def ask_claude_about_github(user_message: str) -> str:
    """
    Send a message to Claude with GitHub tools available.
    Claude can call tools to get information and help you.
    
    Examples:
    - "List all my repositories"
    - "Read the README from my [repo-name]"
    - "Show me open issues in [repo-name]"
    - "Create an issue in [repo-name] titled 'Bug: ...' with description '...'"
    """
    
    client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)
    messages = [{"role": "user", "content": user_message}]
    
    print(f"\n{'='*60}")
    print(f"USER: {user_message}")
    print(f"{'='*60}\n")
    
    # Agentic loop - Claude can call tools multiple times
    while True:
        response = client.messages.create(
            model="claude-opus-4-1",
            max_tokens=4096,
            tools=tools,
            messages=messages
        )
        
        # Check if Claude wants to use tools
        if response.stop_reason == "tool_use":
            # Process all tool calls
            tool_results = []
            
            for content_block in response.content:
                if content_block.type == "tool_use":
                    tool_name = content_block.name
                    tool_input = content_block.input
                    tool_use_id = content_block.id
                    
                    print(f"🔧 Claude calling: {tool_name}")
                    print(f"   Input: {json.dumps(tool_input, indent=2)}\n")
                    
                    # Execute the tool
                    tool_result = handle_tool_call(tool_name, tool_input)
                    
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": tool_use_id,
                        "content": tool_result
                    })
            
            # Add Claude's response and tool results to messages
            messages.append({"role": "assistant", "content": response.content})
            messages.append({"role": "user", "content": tool_results})
        
        else:
            # Claude finished - no more tool calls
            break
    
    # Extract and return the final text response
    final_response = ""
    for content_block in response.content:
        if hasattr(content_block, "text"):
            final_response += content_block.text
    
    print(f"\n{'='*60}")
    print(f"CLAUDE: {final_response}")
    print(f"{'='*60}\n")
    
    return final_response


# ===== EXAMPLES =====

if __name__ == "__main__":
    # Example 1: List repositories
    ask_claude_about_github(
        "Can you list all my GitHub repositories and show me which ones have the most stars?"
    )
    
    # Example 2: Analyze a repository (if you have one)
    # ask_claude_about_github(
    #     "Analyze my 'repo-name' repository and tell me its stats"
    # )
    
    # Example 3: Create an issue
    # ask_claude_about_github(
    #     "Create an issue in 'repo-name' titled 'Feature Request: Add logging' with body 'Add debug logging throughout the app'"
    # )

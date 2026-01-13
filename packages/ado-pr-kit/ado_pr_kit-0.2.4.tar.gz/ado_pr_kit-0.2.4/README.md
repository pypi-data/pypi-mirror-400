# AdoPRKit

[![PyPI version](https://badge.fury.io/py/ado-pr-kit.svg)](https://badge.fury.io/py/ado-pr-kit)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/ado-pr-kit.svg)](https://pypi.org/project/ado-pr-kit/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Model Context Protocol (MCP) server for managing Azure DevOps Pull Requests. Create, review, and manage PRs directly from your AI coding assistant.

## Features

- Create and manage pull requests
- Add comments and review threads
- View diffs and changed files
- Link work items
- Update PR status (draft, publish, abandon)

## Installation

### Local MCP (Recommended)

**Quick start with uvx (no installation):**
```bash
uvx ado-pr-kit
```

**Or install globally:**
```bash
pip install ado-pr-kit
```

**Configure your editor:**

Add to your MCP config (e.g., `mcp_config.json`, `.vscode/mcp.json`, or `claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "ado-pr-kit": {
      "command": "uvx",
      "args": ["ado-pr-kit"],
      "env": {
        "AZDO_ORG_URL": "https://dev.azure.com/your-org",
        "AZDO_PAT": "your-personal-access-token",
        "AZDO_REPO_ID": "your-default-repo"
      }
    }
  }
}
```

> **Note:** `AZDO_REPO_ID` sets your default repository. You can still query any repo by passing `repository_id` to tools.

### Remote MCP (SSE Server)

**Connect to hosted server:**

**Option 1: Native SSE (if your client supports `serverUrl` + `headers`):**

```json
{
  "mcpServers": {
    "ado-pr-kit": {
      "serverUrl": "https://ado-pr-kit.onrender.com/sse",
      "headers": {
        "X-AZDO-ORG-URL": "https://dev.azure.com/your-org",
        "X-AZDO-PAT": "your-personal-access-token",
        "X-AZDO-REPO-ID": "your-default-repo"
      }
    }
  }
}
```

**Option 2: Bridge command (for clients that only support stdio):**

```json
{
  "mcpServers": {
    "ado-pr-kit": {
      "command": "uvx",
      "args": [
        "--from", "ado-pr-kit",
        "ado-pr-connect",
        "--url", "https://ado-pr-kit.onrender.com/sse",
        "--org-url", "https://dev.azure.com/your-org",
        "--pat", "your-personal-access-token",
        "--repo-id", "your-default-repo"
      ]
    }
  }
}
```

**Deploy your own SSE server:**

```bash
uvicorn ado_pr_kit.server_sse:app --host 0.0.0.0 --port 8000
```

Authentication uses HTTP headers:
- `X-AZDO-ORG-URL`: Your Azure DevOps organization URL (required)
- `X-AZDO-PAT`: Your personal access token (required)
- `X-AZDO-REPO-ID`: Default repository ID (required)

## Prerequisites

- Python 3.10+
- Azure DevOps PAT with **Code (Read & Write)** and **Pull Request Threads (Read & Write)** permissions

## Development

```bash
git clone https://github.com/om-surushe/ado-pr-manager.git
cd ado-pr-manager
python3 -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
pytest
```

## Roadmap

- [ ] Inline code comments with file/line context
- [ ] Rich comments (mentions, work item links)
- [ ] Full file content access
- [ ] Work item management (CRUD)
- [ ] PR voting (approve, reject)
- [ ] Pipeline/build status checks

## License

MIT License - see [LICENSE](LICENSE) for details.

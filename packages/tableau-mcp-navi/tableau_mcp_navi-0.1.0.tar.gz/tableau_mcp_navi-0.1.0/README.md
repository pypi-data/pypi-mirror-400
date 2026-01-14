# Tableau MCP Server (tableau-mcp-navi)

A Model Context Protocol (MCP) server for Tableau Server. Enables AI assistants (like Claude, Cursor) to interact with Tableau workbooks, views, datasources, and metadata.

[![PyPI version](https://badge.fury.io/py/tableau-mcp-navi.svg)](https://pypi.org/project/tableau-mcp-navi/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Features

- **22 Tools** for comprehensive Tableau Server interaction
- **Two Authentication Methods**: Personal Access Token (PAT) or Username/Password
- **Metadata API**: Extract refresh info, data lineage, upstream tables
- **Zero Install**: Run directly with `uvx` - no local installation needed
- **Auto Updates**: Users always get the latest version

## Quick Start

### 1. Install uv (if not installed)

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 2. Configure Cursor

Add to `~/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "tableau": {
      "command": "uvx",
      "args": ["tableau-mcp-navi"],
      "env": {
        "TABLEAU_SERVER_URL": "https://your-tableau-server.com",
        "TABLEAU_TOKEN_NAME": "your_token_name",
        "TABLEAU_TOKEN_SECRET": "your_token_secret",
        "TABLEAU_VERIFY_SSL": "false"
      }
    }
  }
}
```

### 3. Restart Cursor

The MCP server will be available immediately!

## Available Tools (22 total)

### Workbook Tools
| Tool | Description |
|------|-------------|
| `list_workbooks` | List all workbooks on the server |
| `get_workbook` | Get workbook details including views |
| `search_workbooks` | Search workbooks by name |

### View Tools
| Tool | Description |
|------|-------------|
| `list_views` | List views (dashboards/sheets) |
| `get_view` | Get view details |
| `get_view_data` | Get underlying data from a view |
| `get_view_image` | Get PNG preview of a view |
| `download_view_image` | Download view image to disk |
| `download_view_image_from_url` | Download image from Tableau URL |

### Data Source Tools
| Tool | Description |
|------|-------------|
| `list_datasources` | List all data sources |
| `get_datasource` | Get data source details |
| `refresh_datasource` | Trigger extract refresh |

### Project Tools
| Tool | Description |
|------|-------------|
| `list_projects` | List all projects |
| `get_project` | Get project details |

### User Tools
| Tool | Description |
|------|-------------|
| `list_users` | List users on the server |
| `get_user` | Get user details |

### Metadata API Tools (RCA & Lineage)
| Tool | Description |
|------|-------------|
| `get_datasource_extract_info` | Get extract refresh times |
| `get_dashboard_extract_info` | Get extract info for all datasources in a dashboard |
| `find_stale_extracts` | Find datasources with stale extracts |
| `get_datasource_tables` | Get upstream tables for a datasource |
| `get_dashboard_tables` | Get ALL tables powering a dashboard |
| `get_dashboard_sql_from_url` | Extract custom SQL from dashboard URL |

### Other Tools
| Tool | Description |
|------|-------------|
| `test_connection` | Test Tableau connectivity |
| `list_sites` | List available sites |

## Configuration

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `TABLEAU_SERVER_URL` | ✅ | Your Tableau Server URL |
| `TABLEAU_TOKEN_NAME` | ✅* | Personal Access Token name |
| `TABLEAU_TOKEN_SECRET` | ✅* | Personal Access Token secret |
| `TABLEAU_USERNAME` | ✅* | Username (alternative to PAT) |
| `TABLEAU_PASSWORD` | ✅* | Password (alternative to PAT) |
| `TABLEAU_SITE_ID` | ❌ | Site ID (empty for default) |
| `TABLEAU_VERIFY_SSL` | ❌ | Set to "false" for self-signed certs |
| `TABLEAU_API_VERSION` | ❌ | Override API version |
| `TABLEAU_MCP_ANALYTICS` | ❌ | Set to "false" to disable analytics |

*Either PAT or Username/Password required

### Getting a Personal Access Token

1. Log in to Tableau Server
2. Click your profile icon → **My Account Settings**
3. Scroll to **Personal Access Tokens**
4. Click **Create new token**
5. Copy both the **Token Name** and **Token Secret**

## Usage Examples

After configuring Cursor:

```
"List all workbooks in Tableau"
"Get details for workbook abc123"
"Search for workbooks about sales"
"Get data from view xyz789"
"What tables power the Sales Dashboard?"
"Find all stale extracts older than 48 hours"
"Get the SQL from this Tableau URL: https://..."
```

## Updates

When the package is updated on PyPI, users automatically get the new version on their next run - no action required!

## Development

```bash
# Clone
git clone https://github.com/manish-coder-1007/tableau-mcp-navi.git
cd tableau-mcp-navi

# Install dependencies
uv sync

# Run locally
uv run python -m tableau_mcp_navi
```

## License

MIT License - see [LICENSE](LICENSE) file.

## Author

Manish Balot

## Links

- [GitHub Repository](https://github.com/manish-coder-1007/tableau-mcp-navi)
- [PyPI Package](https://pypi.org/project/tableau-mcp-navi/)
- [Report Issues](https://github.com/manish-coder-1007/tableau-mcp-navi/issues)

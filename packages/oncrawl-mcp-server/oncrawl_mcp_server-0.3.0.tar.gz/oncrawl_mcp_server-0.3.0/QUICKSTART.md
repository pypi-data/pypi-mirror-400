# Quick Start Guide

Get your OnCrawl MCP server running in 5 minutes.

## Step 1: Get Your OnCrawl API Token

1. Log into [OnCrawl](https://app.oncrawl.com)
2. Go to **Settings** → **API**
3. Click **Create New Token**
4. Give it a name (e.g., "Claude MCP")
5. Select scope: `projects:read`
6. **Copy the token** - you'll need it for configuration

## Step 2: Find Your Workspace ID

Look at your OnCrawl URL when logged in:
```
https://app.oncrawl.com/workspaces/abc123xyz/projects
                                    ^^^^^^^^^
                              This is your workspace ID
```

## Step 3: Setup the MCP Server

### Option A: Using Claude Code CLI

```bash
# Navigate to the project directory
cd "c:\Users\Antonio\Oncrawl MCP"

# Create virtual environment (if not already done)
python -m venv .venv

# Activate it
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Install the package in development mode (so it can be run as a module)
pip install -e .

# Add to Claude Code config
claude mcp add oncrawl
```

Then edit the config file at `~/.config/claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "oncrawl": {
      "command": "C:\\Users\\Antonio\\Oncrawl MCP\\.venv\\Scripts\\python.exe",
      "args": ["-m", "oncrawl_mcp_server.server"],
      "env": {
        "ONCRAWL_API_TOKEN": "04Q56SGGKZVXAZFKUR9JC0Q5GZCOAY1VA6O05POX"
      }
    }
  }
}
```

### Option B: Using Claude Desktop

Edit the config at:
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **Mac**: `~/Library/Application Support/Claude/claude_desktop_config.json`

Add:
```json
{
  "mcpServers": {
    "oncrawl": {
      "command": "C:\\Users\\Antonio\\Oncrawl MCP\\.venv\\Scripts\\python.exe",
      "args": ["-m", "oncrawl_mcp_server.server"],
      "env": {
        "ONCRAWL_API_TOKEN": "your-token-here"
      }
    }
  }
}
```

**Important**: Use full absolute paths!

## Step 4: Restart Claude

- **Claude Code**: Restart the CLI
- **Claude Desktop**: Restart the application

## Step 5: Test It!

Try asking Claude:

```
"List my OnCrawl projects in workspace YOUR_WORKSPACE_ID"
```

Or for a full analysis:

```
"I want to analyze my website's SEO structure. First, list my OnCrawl
projects in workspace YOUR_WORKSPACE_ID, then get the latest crawl from
the first project and show me the overall structure."
```

## Common First Queries

Once you have a crawl ID:

```
"Get the schema for crawl CRAWL_ID so I know what fields are available"

"Show me pages with depth > 5"

"Find all pages with no internal links (orphan pages)"

"What's the distribution of status codes on this site?"

"Find pages in /blog/ with fewer than 3 inlinks"
```

## Troubleshooting

### MCP server not showing up

1. Check the paths in your config are absolute (full paths)
2. Verify the virtual environment has dependencies: `pip list | grep mcp`
3. Check Claude's logs for errors
4. Make sure you restarted Claude after config changes

### API authentication errors

1. Verify your token is correct
2. Check the token has `projects:read` scope
3. Make sure it's set in the `env` section of the config

### Can't find workspace/project IDs

1. Log into OnCrawl web interface
2. The URL shows your workspace ID
3. Use `oncrawl_list_projects` with your workspace ID to find projects
4. Use `oncrawl_get_project` to get crawl IDs for a project

## Next Steps

See [README.md](README.md) for:
- Complete tool reference
- OQL query examples
- Advanced usage patterns
- Combining with Google Search Console MCP

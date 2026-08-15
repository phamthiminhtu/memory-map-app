The MCP (Model Context Protocol) server allows external AI tools like Claude Desktop to search and manage your memories.

#### Prerequisites

Install MCP dependencies:
```bash
pip install mcp
```

#### Configure Claude Desktop

1. Locate your Claude Desktop config file:
   - **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
   - **Linux**: `~/.config/Claude/claude_desktop_config.json`

2. Add the memory-map server configuration:
```json
{
  "mcpServers": {
    "memory-map": {
      "command": "/Users/tototus/workspace/memory-map-env/bin/python",
      "args": [
        "/Users/tototus/workspace/memory-map-app/mcp_server/server.py"
      ],
      "env": {
        "PYTHONPATH": "/Users/tototus/workspace/memory-map-app"
      }
    }
  }
}
```

**Important**: Update both paths to match your actual installation:
- `command`: Path to Python in your virtual environment (`~/workspace/memory-map-env/bin/python`)
- `args[0]`: Path to the MCP server script
- `env.PYTHONPATH`: Path to your project root directory

3. Restart Claude Desktop

4. The memory-map tools should now be available in Claude Desktop

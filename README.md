# TIDAL MCP - Simplified Architecture

A clean, minimal implementation of a TIDAL Model Context Protocol (MCP) server for music discovery and playlist management.

## Features

- 🔍 **Track Search** - Search TIDAL's music catalog
- 🎵 **Playlist Management** - Create and manage playlists  
- ❤️ **Favorites Access** - Get your favorite tracks
- 📚 **Playlist Browsing** - View tracks in any playlist
- 🔐 **OAuth Authentication** - Secure browser-based login with session persistence
- ⚡ **Minimal Dependencies** - Only `mcp[cli]` and `tidalapi`
- 🚀 **FastMCP Framework** - Clean, efficient MCP implementation

## Quick Start

```bash
# Clone the repository
cd /path/to/tidal-mcp

# Install dependencies
uv sync

# Install in editable mode
uv pip install -e .

# Test with MCP Inspector
npx @modelcontextprotocol/inspector uv run tidal-mcp
```

The inspector will:
1. Start on `http://localhost:6274`
2. Open your browser automatically
3. Click "Connect" to establish connection
4. All 7 TIDAL tools will be available

## Available Tools

| Tool | Description | Parameters |
|------|-------------|------------|
| `login` | Authenticate with TIDAL via OAuth | None |
| `search_tracks` | Search TIDAL's music catalog | `query` (string), `limit` (int, max 50) |
| `get_favorites` | Get user's favorite tracks | `limit` (int, default 20) |
| `create_playlist` | Create a new playlist | `name` (string), `description` (string, optional) |
| `add_tracks_to_playlist` | Add tracks to existing playlist | `playlist_id` (string), `track_ids` (list of strings) |
| `get_user_playlists` | List user's playlists | `limit` (int, default 20) |
| `get_playlist_tracks` | Get tracks from a playlist | `playlist_id` (string), `limit` (int, default 100) |

## Claude Desktop Configuration

Add to your Claude Desktop configuration file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "tidal-mcp": {
      "command": "/full/path/to/uv",
      "args": [
        "--directory", "/path/to/tidal-mcp",
        "run", "tidal-mcp"
      ]
    }
  }
}
```

**Important**: Use the full path to `uv` (e.g., `/Users/username/.local/bin/uv` on macOS). Find it with:
```bash
which uv
```

## Architecture

Single-file MCP server with direct TIDAL API integration:
- **FastMCP Framework** - Handles MCP protocol efficiently
- **Direct tidalapi Integration** - No intermediate layers
- **Session Persistence** - OAuth tokens saved to `.tidal-sessions/` (gitignored)
- **Clean JSON Output** - No debug messages to stdout

## Usage Examples

### Basic Workflow
1. **Authenticate**: Run `login` tool (opens browser for OAuth)
2. **Search Music**: `search_tracks("Radiohead", 10)`
3. **Create Playlist**: `create_playlist("My Mix", "Best tracks")`
4. **Add Tracks**: `add_tracks_to_playlist(playlist_id, [track_ids])`

### Search Tips
- Simple queries work best: `"Radiohead"` or `"Creep"`
- Artist + Song: `"Radiohead Paranoid Android"`
- Avoid complex multi-term searches

## Troubleshooting

### Connection Issues
If the MCP Inspector shows connection errors:
1. Ensure no other processes are using ports 6274 or 6277
2. Kill any stale processes: `pkill -f "tidal-mcp"`
3. Restart the inspector

### Authentication Issues
If login fails or session expires:
```bash
# Remove old session file
rm -rf .tidal-sessions/

# Run login tool again
```

### Port Conflicts
```bash
# Check if ports are in use
lsof -i :6274 -i :6277

# Kill processes using the ports
kill <PID>
```

## Development

### Project Structure
```
tidal-mcp/
├── README.md                 # This file
├── pyproject.toml           # Package configuration
├── CLAUDE.md                # Development guidance
└── src/
    └── tidal_mcp/
        ├── __init__.py      # Package init
        └── server.py        # Complete MCP server
```

### Testing
```bash
# Test server directly (outputs JSON)
echo '{"jsonrpc": "2.0", "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "test", "version": "1.0.0"}}, "id": 1}' | uv run tidal-mcp

# Interactive testing with Inspector
npx @modelcontextprotocol/inspector uv run tidal-mcp
```

## TODO: Missing Playlist Editing Features

Based on testing (2025-08-11), the following playlist editing capabilities are not yet implemented:

### High Priority
- **Remove tracks from playlist** - Remove specific tracks by ID or position
- **Reorder playlist tracks** - Move tracks within a playlist
- **Insert tracks at position** - Add tracks at specific positions (currently only appends)

### Medium Priority  
- **Update playlist details** - Edit playlist name, description, or privacy settings
- **Delete playlist** - Permanently delete a playlist
- **Clear playlist** - Remove all tracks from a playlist

### Low Priority
- **Duplicate playlist** - Create a copy of an existing playlist
- **Merge playlists** - Combine tracks from multiple playlists
- **Playlist collaboration** - Share editing permissions with other users

These features would require extending the TIDAL API integration in `server.py`. The current implementation provides basic functionality (create, add tracks, view) but lacks advanced editing capabilities needed for full playlist management.

## TODO: FastMCP Best Practices Improvements

The following enhancements would align the server with FastMCP 2.11+ best practices:

### Code Architecture
- **Async Operations** - Convert tools to async functions for better performance
- **Structured Output Schemas** - Use Pydantic models for type-safe responses
- **Context State Management** - Replace global session with FastMCP Context
- **Middleware Support** - Add logging, rate limiting, or auth middleware
- **Environment Configuration** - Support settings and environment variables

### Implementation Quality
- **Error Handling** - Implement more granular error types and responses
- **Input Validation** - Add comprehensive parameter validation
- **Testing Suite** - Create unit and integration tests
- **Documentation** - Add API documentation and type hints
- **Performance** - Optimize for concurrent requests and caching

## Requirements

- Python 3.10+
- uv package manager
- TIDAL account (free or premium)

## License

MIT
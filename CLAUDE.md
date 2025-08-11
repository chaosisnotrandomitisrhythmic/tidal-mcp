# CLAUDE.md

This file provides guidance to Claude when working with the TIDAL MCP project.

## Project Overview

TIDAL MCP is a simplified Model Context Protocol server for TIDAL music integration. It provides clean, direct access to TIDAL's music catalog and playlist management features through Claude Desktop or any MCP-compatible client.

**Architecture Philosophy**: Minimal, single-process design with direct API integration using FastMCP framework.

## Project Structure

```
tidal-mcp/
├── README.md                 # User-facing documentation
├── pyproject.toml           # Python project configuration
├── CLAUDE.md                # This file - AI development guidance
└── src/
    └── tidal_mcp/
        ├── __init__.py      # Package initialization
        └── server.py        # Complete MCP server implementation
```

## Key Implementation Details

### FastMCP Integration
The server uses FastMCP for clean MCP protocol handling:
```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("TIDAL MCP")

@mcp.tool()
def tool_name(...):
    # Tool implementation
```

### Entry Point Configuration
**IMPORTANT**: The entry point in `pyproject.toml` must point to `mcp.run`:
```toml
[project.scripts]
tidal-mcp = "tidal_mcp.server:mcp.run"
```

### No Print Statements to Stdout
**CRITICAL**: MCP servers must ONLY output JSON to stdout. Any debug messages break the protocol:
```python
# WRONG - breaks MCP protocol
def main():
    print("Starting server...")  # NO!
    
# CORRECT - clean implementation
def main():
    pass  # FastMCP handles everything
```

## Dependencies

**Minimal dependency policy** - only essential packages:

- `mcp[cli]>=1.6.0` - Model Context Protocol framework with FastMCP
- `tidalapi>=0.8.3` - TIDAL API client library

## Development Commands

### Setup and Installation
```bash
# Install dependencies
uv sync

# Install in editable mode for development
uv pip install -e .
```

### Running the Server
```bash
# Run MCP server directly (outputs JSON only)
uv run tidal-mcp

# Test with MCP Inspector
npx @modelcontextprotocol/inspector uv run tidal-mcp

# Quick protocol test
echo '{"jsonrpc": "2.0", "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "test", "version": "1.0.0"}}, "id": 1}' | uv run tidal-mcp
```

### Troubleshooting Port Conflicts
```bash
# Check for processes using MCP ports
lsof -i :6274 -i :6277

# Kill specific process
kill <PID>

# Kill all MCP-related processes
pkill -f "npx.*inspector"
pkill -f "tidal-mcp"
```

## Core Functionality

### Authentication Flow
1. Uses `tidalapi.Session.login_oauth()` for browser-based OAuth
2. Session persisted to: `/var/folders/*/T/tidal-mcp-v2-session.json`
3. Automatic session reuse on subsequent runs
4. No manual token management required

### Available MCP Tools

| Tool | Purpose | Key Parameters |
|------|---------|----------------|
| `login` | OAuth authentication | None |
| `search_tracks` | Search music catalog | `query`, `limit` (max 50) |
| `get_favorites` | Get favorite tracks | `limit` |
| `create_playlist` | Create new playlist | `name`, `description` |
| `add_tracks_to_playlist` | Add tracks to playlist | `playlist_id`, `track_ids[]` |
| `get_user_playlists` | List user playlists | `limit` |
| `get_playlist_tracks` | Get playlist tracks | `playlist_id`, `limit` |

### Search Behavior
Based on testing, TIDAL search works best with:
- Single artist names: `"Radiohead"`
- Artist + song: `"Radiohead Creep"`
- Song titles: `"Paranoid Android"`
- Avoid complex queries: `"Artist Album Song Year"` often fails

## Technical Architecture

### Session Management
```python
# Global session - simple and effective
session = tidalapi.Session()
SESSION_FILE = Path(tempfile.gettempdir()) / "tidal-mcp-session.json"

def ensure_authenticated() -> bool:
    """Check authentication - used by all tools"""
    if SESSION_FILE.exists():
        session.load_session_from_file(SESSION_FILE)
    return session.check_login()
```

### Error Handling Pattern
```python
@mcp.tool()
def tool_name(param: str) -> dict:
    # Always check authentication first
    if not ensure_authenticated():
        return {
            "status": "error",
            "message": "Not authenticated. Please run the 'login' tool first.",
        }
    
    try:
        # Tool logic here
        return {
            "status": "success",
            "data": result
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Operation failed: {str(e)}"
        }
```

### Data Formatting
```python
# Standard track format across all tools
{
    "id": str(track.id),
    "title": track.name,
    "artist": track.artist.name if track.artist else "Unknown Artist",
    "album": track.album.name if track.album else "Unknown Album",
    "duration_seconds": track.duration,
    "url": f"https://tidal.com/browse/track/{track.id}"
}
```

## Claude Desktop Configuration

Add to Claude Desktop config file:

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

**IMPORTANT**: Claude Desktop requires the full path to `uv` because it doesn't inherit your shell's PATH. Find your uv path with:
```bash
which uv  # Usually /Users/username/.local/bin/uv on macOS
```

## Common Use Cases

### Music Discovery Workflow
```python
# 1. Authenticate
login()

# 2. Search for music
results = search_tracks("Radiohead", 10)

# 3. Create playlist
playlist = create_playlist("Radiohead Mix", "My favorite Radiohead tracks")

# 4. Add tracks
track_ids = [track["id"] for track in results["tracks"]]
add_tracks_to_playlist(playlist["playlist"]["id"], track_ids)
```

### Playlist Management
```python
# List playlists
playlists = get_user_playlists(20)

# Get tracks from specific playlist
tracks = get_playlist_tracks(playlist_id, 100)

# Get favorite tracks
favorites = get_favorites(50)
```

## Troubleshooting Guide

### Issue: "Connection Error" in MCP Inspector

**Cause**: Server is outputting non-JSON to stdout

**Solution**: 
1. Remove ALL print statements from server.py
2. Ensure entry point is `mcp.run` not `main`
3. Reinstall: `uv pip install -e .`

### Issue: Authentication Fails

**Solution**:
```bash
# Delete session file
rm /var/folders/*/T/tidal-mcp-session.json

# Run login tool again
```

### Issue: Port Already in Use

**Solution**:
```bash
# Find and kill processes
lsof -i :6274 -i :6277
kill <PID>

# Or kill all MCP processes
pkill -f "inspector|tidal-mcp"
```

### Issue: Search Returns No Results

**Solution**:
- Simplify query (single artist or song name)
- Check spelling
- Verify authentication status

## Design Principles

1. **Simplicity First** - Minimal code, maximum functionality
2. **Clean Protocol** - JSON-only stdout, no debug prints
3. **Direct Integration** - No unnecessary layers or abstractions  
4. **Robust Error Handling** - Clear, actionable error messages
5. **Session Persistence** - Seamless authentication experience
6. **Standard Formatting** - Consistent data structures across tools

## Testing Checklist

### Pre-release Testing
- [ ] Server outputs only JSON to stdout
- [ ] All tools return proper error when not authenticated
- [ ] Login flow opens browser and saves session
- [ ] Search returns results for common queries
- [ ] Playlist creation works
- [ ] Adding tracks to playlist succeeds
- [ ] Session persists across restarts
- [ ] MCP Inspector can connect and list tools
- [ ] Claude Desktop can use the server

### Integration Testing
```bash
# 1. Clean start
rm /var/folders/*/T/tidal-mcp-session.json

# 2. Test with inspector
npx @modelcontextprotocol/inspector uv run tidal-mcp

# 3. Run through complete workflow:
#    - Login
#    - Search
#    - Create playlist
#    - Add tracks
#    - Verify playlist contents
```

## Future Enhancements

When adding features, maintain the minimalist approach:
- Add tools only for core use cases
- Keep dependencies minimal
- Maintain direct TIDAL API integration
- Preserve single-file architecture if possible
- Always test with MCP Inspector before release

## Code Style

- Use FastMCP decorators for all tools
- Consistent error response format
- Type hints where helpful
- Clear docstrings for each tool
- Format with black/isort if needed

Remember: This project prioritizes **simplicity**, **reliability**, and **clean MCP protocol implementation**. No overengineering!
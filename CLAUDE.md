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
        ├── models.py        # Pydantic models for structured outputs
        └── server.py        # MCP server implementation
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
2. Session persisted to: `<project_root>/.tidal-sessions/session.json`
3. Automatic session reuse on subsequent runs
4. No manual token management required
5. Session files are gitignored for security

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
PROJECT_ROOT = Path(__file__).parent.parent.parent
SESSION_DIR = PROJECT_ROOT / ".tidal-sessions"
SESSION_DIR.mkdir(parents=True, exist_ok=True)
SESSION_FILE = SESSION_DIR / "session.json"

def ensure_authenticated() -> bool:
    """Check authentication - used by all tools"""
    if SESSION_FILE.exists():
        session.load_session_from_file(SESSION_FILE)
    return session.check_login()
```

### Error Handling Pattern
```python
from .models import ErrorResult, TrackList

@mcp.tool()
def tool_name(param: str) -> TrackList | ErrorResult:
    # Always check authentication first
    if not ensure_authenticated():
        return ErrorResult(
            message="Not authenticated. Please run the 'login' tool first."
        )
    
    try:
        # Tool logic here
        return TrackList(
            status="success",
            tracks=tracks,
            count=len(tracks)
        )
    except Exception as e:
        return ErrorResult(
            message=f"Operation failed: {str(e)}"
        )
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
rm .tidal-sessions/session.json

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

### Issue: "LoggedInUser.playlists() got an unexpected keyword argument 'limit'"

**Cause**: TIDAL API doesn't support limit parameter on user playlists endpoint

**Solution**: 
- Issue fixed in server.py - now uses client-side limiting
- Fetches all playlists first, then applies limit via array slicing
- Pattern: `all_playlists = session.user.playlists(); limited = all_playlists[:limit]`

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
rm -rf .tidal-sessions/

# 2. Test with inspector
npx @modelcontextprotocol/inspector uv run tidal-mcp

# 3. Run through complete workflow:
#    - Login
#    - Search
#    - Create playlist
#    - Add tracks
#    - Verify playlist contents
```

## TODO: Essential Playlist Features

For single-user use, these playlist editing features would be genuinely useful:

### Features Worth Implementing

1. **`remove_tracks_from_playlist`**
   - Parameters: `playlist_id`, `track_ids[]` or `positions[]`
   - Remove specific tracks by ID or position
   - Essential for playlist curation

2. **`reorder_playlist_tracks`**
   - Parameters: `playlist_id`, `from_position`, `to_position`
   - Move tracks within playlist
   - Important for organizing playlists

3. **`update_playlist_details`**
   - Parameters: `playlist_id`, `name`, `description`
   - Update playlist metadata
   - Basic renaming functionality

4. **`delete_playlist`**
   - Parameters: `playlist_id`
   - Permanently delete a playlist
   - Basic cleanup functionality

### Implementation Notes
- Keep synchronous implementation (no async needed for single-user)
- Maintain current simple error handling pattern
- Test with MCP Inspector before use
- Preserve the single-file architecture if possible

## Design Principles for Single-User Use

This project is optimized for personal use and intentionally avoids overengineering:

### What We Keep Simple
- ✅ **Synchronous operations** - No async complexity needed for single-user
- ✅ **Global session management** - Works perfectly for personal use
- ✅ **Direct TIDAL API integration** - No unnecessary abstraction layers
- ✅ **Structured Output Schemas** - Pydantic models already implemented
- ✅ **Minimal dependencies** - Only `mcp[cli]` and `tidalapi`
- ✅ **Single-file architecture** - Easy to understand and maintain

### What We Intentionally Avoid
- ❌ Async/await complexity (not needed for single-user)
- ❌ Complex state management (global session works fine)
- ❌ Middleware layers (unnecessary for personal use)
- ❌ Environment configurations (hardcoded settings are fine)
- ❌ Extensive testing suites (manual testing sufficient)
- ❌ Performance optimizations (not needed at this scale)

## Code Style

- Use FastMCP decorators for all tools
- Consistent error response format
- Type hints where helpful
- Clear docstrings for each tool
- Format with black/isort if needed

Remember: This project prioritizes **simplicity**, **reliability**, and **clean MCP protocol implementation**. No overengineering!
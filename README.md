# TIDAL MCP

Async-first TIDAL Model Context Protocol server for music discovery and playlist management. Built with FastMCP 2.12+ for stability and performance.

## Features

- 🔍 Track search with async operations
- 🎵 Playlist creation and management  
- ❤️ Favorites access
- 🔐 OAuth authentication with session persistence
- ⚡ FastMCP 2.12+ with async/await architecture
- 🚀 Non-blocking I/O for all TIDAL API operations
- 🎯 Clean error handling with ToolError exceptions

## Quick Start

```bash
# Install dependencies (including anyio for async support)
cd /path/to/tidal-mcp
uv sync
uv pip install -e .

# Test with MCP Inspector
npx @modelcontextprotocol/inspector uv run tidal-mcp

# Quick protocol test
echo '{"jsonrpc": "2.0", "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "test", "version": "1.0.0"}}, "id": 1}' | uv run tidal-mcp
```

## Available Tools

| Tool | Description | Parameters |
|------|-------------|------------|
| `login` | OAuth authentication | None |
| `search_tracks` | Search catalog | `query`, `limit` (max 50) |
| `get_favorites` | Get favorite tracks | `limit` (default 20) |
| `create_playlist` | Create playlist | `name`, `description` (optional) |
| `add_tracks_to_playlist` | Add tracks | `playlist_id`, `track_ids` |
| `get_user_playlists` | List playlists | `limit` (default 20) |
| `get_playlist_tracks` | Get playlist tracks | `playlist_id`, `limit` (default 100) |

## Claude Desktop Configuration

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`  
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "tidal-mcp": {
      "command": "/full/path/to/uv",
      "args": ["--directory", "/path/to/tidal-mcp", "run", "tidal-mcp"]
    }
  }
}
```

Find your `uv` path: `which uv`

## The Paradise Garage Tutorial

![Disco Ball](./assets/Art%20Disco%20Ball%20GIF%20by%20mr.%20div.gif)

*This tutorial is designed for use with Claude Desktop after you've configured the MCP server.*

### Philosophy

Build playlists as emotional journeys, not random collections. Think Larry Levan's Saturday night ritual - constructing arcs from midnight to sunrise.

### Step 1: Research

Open Claude Desktop and start with context before tools:

```
"Tell me about Paradise Garage era and Larry Levan's approach to DJing.
What labels and artists defined that sound?"
```

### Step 2: Build

In a new Claude Desktop conversation, deploy with specific intent:

```
You have Tidal MCP access. Build a Paradise Garage playlist from midnight to sunrise.

Start with dubby hypnotics (Dinosaur L, Loose Joints). 
Move through gospel-disco (First Choice, Loleatta Holloway). 
Peak with proto-house (Peech Boys, Class Action). 
Close with cosmic dubs (Grace Jones, Manuel Göttsching).

When tracks aren't available, find emotional equivalents. 
The flow is sacred - every substitution must maintain the arc.
```

### What Happens

1. **Authenticate** - Browser opens for TIDAL login (first time only)
2. **Search** - Hunts for tracks, tries variations
3. **Substitute** - Finds emotional equivalents when needed
4. **Build** - Creates playlist with proper sequencing

### Pro Tips: Fun Ideas to Try

**Iterate**: `"Need more gospel energy in the middle section"`

**Genre Jump** - Explore other legendary sessions: 
- Ron Hardy Music Box - darker, more aggressive
- David Mancuso Loft - earlier, eclectic, audiophile

**Modern Connections**: `"Show the DNA from Levan to Moodymann to Palms Trax"`

Remember: You're creating what Levan called "a feeling." Every track earns its place.

---

*Pure magic. Build something that would make the heads at King Street proud.*

## Architecture

### Technical Stack
- **Framework**: FastMCP 2.12+ with async/await support
- **Async Runtime**: anyio for thread pool execution
- **TIDAL Integration**: tidalapi library (synchronous, wrapped with anyio.to_thread)
- **Error Handling**: FastMCP ToolError exceptions for clean protocol errors
- **Session Management**: OAuth tokens persisted in `.tidal-sessions/`
- **Data Models**: Pydantic schemas for structured outputs

### Key Design Patterns
- All MCP tools are async functions for non-blocking I/O
- Blocking tidalapi operations run in thread pool via `anyio.to_thread.run_sync()`
- Global session instance with async authentication checks
- Clean separation between MCP protocol layer and TIDAL API layer

## Troubleshooting

**Authentication Issues**
```bash
rm -rf .tidal-sessions/
# Run login tool again
```

**Port Conflicts**
```bash
lsof -i :6274 -i :6277
kill <PID>
```

## Requirements

- Python 3.10+
- uv package manager
- TIDAL account (free or premium)

## Development

```
tidal-mcp/
├── pyproject.toml          # Dependencies: fastmcp, tidalapi, anyio
├── README.md              # This file
├── CLAUDE.md              # AI development guidance
└── src/
    └── tidal_mcp/
        ├── __init__.py
        ├── models.py      # Pydantic models for structured outputs
        └── server.py
```

**Testing**
```bash
# Direct test
echo '{"jsonrpc": "2.0", "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "test", "version": "1.0.0"}}, "id": 1}' | uv run tidal-mcp

# Interactive
npx @modelcontextprotocol/inspector uv run tidal-mcp
```

## TODO

- Remove tracks from playlist
- Reorder playlist tracks
- Update playlist details
- Delete playlist

## Requirements

- Python 3.10+
- uv package manager
- TIDAL account

## License

MIT
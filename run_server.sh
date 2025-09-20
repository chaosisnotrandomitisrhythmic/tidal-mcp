#!/bin/bash
# Wrapper script for TIDAL MCP to ensure clean output for Claude Desktop

# Unset VIRTUAL_ENV to avoid uv warnings
unset VIRTUAL_ENV

# Get the directory of this script
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Run the server, suppressing stderr warnings
exec /Users/chaosisnotrandomitisrythmic/.local/bin/uv --directory "$DIR" run tidal-mcp 2>/dev/null
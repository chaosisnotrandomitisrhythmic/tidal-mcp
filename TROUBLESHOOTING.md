# TIDAL MCP Troubleshooting Guide

## Common Issues and Solutions

### Issue: "No result received from client-side tool execution" in Claude Desktop

**Solution 1: Use the wrapper script**

We've created a wrapper script that suppresses stderr warnings that can interfere with Claude Desktop:

```bash
# Already configured in your Claude Desktop config:
/Users/chaosisnotrandomitisrythmic/mcp-servers/tidal-mcp/run_server.sh
```

**Solution 2: Restart Claude Desktop**

After configuration changes:
1. Quit Claude Desktop completely (Cmd+Q)
2. Restart Claude Desktop
3. Open a new conversation
4. Try: "Use tidal-mcp to search for Radiohead songs"

### Issue: Authentication Required

**First Time Setup:**
1. In Claude Desktop, type: "Use tidal-mcp login tool"
2. Browser will open for TIDAL OAuth
3. Complete login in browser
4. Session is saved for future use

**Session Expired:**
```bash
# Remove old session
rm -rf /Users/chaosisnotrandomitisrythmic/mcp-servers/tidal-mcp/.tidal-sessions/

# Then use login tool again in Claude Desktop
```

### Issue: Server Not Starting

**Check if server runs standalone:**
```bash
# Test basic initialization
echo '{"jsonrpc": "2.0", "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "test", "version": "1.0.0"}}, "id": 1}' | /Users/chaosisnotrandomitisrythmic/mcp-servers/tidal-mcp/run_server.sh
```

**Expected output:**
Should return JSON with `"name": "TIDAL MCP"`

### Issue: Virtual Environment Conflicts

**Symptom:** Warning about VIRTUAL_ENV mismatch

**Solution:** The wrapper script (`run_server.sh`) handles this by unsetting VIRTUAL_ENV

### Testing the Server

**Quick Protocol Test:**
```bash
python /Users/chaosisnotrandomitisrythmic/mcp-servers/tidal-mcp/test_protocol.py
```

**MCP Inspector Test:**
```bash
npx @modelcontextprotocol/inspector /Users/chaosisnotrandomitisrythmic/mcp-servers/tidal-mcp/run_server.sh
```

### Claude Desktop Configuration

**Verify configuration:**
```bash
cat ~/Library/Application\ Support/Claude/claude_desktop_config.json | grep -A5 "tidal-mcp"
```

**Should show:**
```json
"tidal-mcp": {
  "command": "/Users/chaosisnotrandomitisrythmic/mcp-servers/tidal-mcp/run_server.sh",
  "args": []
}
```

### Tool Usage in Claude Desktop

**Correct usage examples:**

1. **Search for music:**
   "Use tidal-mcp to search for songs by Radiohead"

2. **Create playlist:**
   "Use tidal-mcp to create a playlist called 'Chill Vibes' and add some ambient tracks"

3. **Get favorites:**
   "Use tidal-mcp to show my favorite tracks"

### Debug Mode

To see what's happening behind the scenes:

```bash
# Run server with stderr visible
/Users/chaosisnotrandomitisrythmic/.local/bin/uv --directory /Users/chaosisnotrandomitisrythmic/mcp-servers/tidal-mcp run tidal-mcp
```

Then send test commands to see both stdout (JSON) and stderr (debug info).

## Architecture Notes

- Server uses FastMCP 2.12+ with async/await
- All TIDAL operations run in thread pool (anyio.to_thread)
- OAuth tokens persist in `.tidal-sessions/`
- Tools raise ToolError exceptions for clean error handling

## If All Else Fails

1. Check that all dependencies are installed:
   ```bash
   cd /Users/chaosisnotrandomitisrythmic/mcp-servers/tidal-mcp
   uv sync
   uv pip install -e .
   ```

2. Verify Python version (needs 3.10+):
   ```bash
   uv run python --version
   ```

3. Test with MCP Inspector for detailed debugging:
   ```bash
   npx @modelcontextprotocol/inspector /Users/chaosisnotrandomitisrythmic/mcp-servers/tidal-mcp/run_server.sh
   ```

4. Check Claude Desktop logs:
   - Help menu → Show Logs
   - Look for tidal-mcp related errors
import json
import subprocess
import sys

# Test sequence
test_messages = [
    {"jsonrpc": "2.0", "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "test", "version": "1.0.0"}}, "id": 1},
    {"jsonrpc": "2.0", "method": "initialized", "params": {}},
    {"jsonrpc": "2.0", "method": "tools/list", "id": 2}
]

# Run the server
cmd = [
    "/Users/chaosisnotrandomitisrythmic/.local/bin/uv",
    "--directory", "/Users/chaosisnotrandomitisrythmic/mcp-servers/tidal-mcp",
    "run", "tidal-mcp"
]

# Remove VIRTUAL_ENV to avoid warning
import os
env = os.environ.copy()
if 'VIRTUAL_ENV' in env:
    del env['VIRTUAL_ENV']

proc = subprocess.Popen(
    cmd,
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.DEVNULL,  # Suppress stderr warnings
    text=True,
    env=env
)

# Send messages
for msg in test_messages:
    proc.stdin.write(json.dumps(msg) + '\n')
    proc.stdin.flush()

# Get responses
for i in range(2):  # We expect 2 responses (init and tools/list)
    line = proc.stdout.readline()
    if line:
        response = json.loads(line)
        if 'result' in response:
            if 'serverInfo' in response['result']:
                print(f"✅ Server initialized: {response['result']['serverInfo']['name']}")
            elif 'tools' in response['result']:
                tools = response['result']['tools']
                print(f"✅ Found {len(tools)} tools:")
                for tool in tools[:3]:  # Show first 3
                    print(f"   - {tool['name']}")
        elif 'error' in response:
            print(f"Response: {json.dumps(response, indent=2)}")

proc.terminate()

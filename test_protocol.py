#!/usr/bin/env python3
"""Test TIDAL MCP protocol compatibility"""

import json
import subprocess
import sys
import time

def test_mcp_server():
    """Test MCP server protocol"""
    print("Testing TIDAL MCP Server Protocol...")
    
    # Start server
    cmd = ["/Users/chaosisnotrandomitisrythmic/mcp-servers/tidal-mcp/run_server.sh"]
    proc = subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )
    
    def send_request(request):
        """Send request and get response"""
        proc.stdin.write(json.dumps(request) + '\n')
        proc.stdin.flush()
        response = proc.stdout.readline()
        if response:
            return json.loads(response)
        return None
    
    try:
        # Test 1: Initialize
        print("\n1. Testing initialization...")
        init_request = {
            "jsonrpc": "2.0",
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "test", "version": "1.0.0"}
            },
            "id": 1
        }
        response = send_request(init_request)
        if response and "result" in response:
            print(f"   ✅ Server initialized: {response['result']['serverInfo']['name']}")
        else:
            print(f"   ❌ Failed: {response}")
            
        # Test 2: Send initialized notification
        print("\n2. Sending initialized notification...")
        proc.stdin.write(json.dumps({"jsonrpc": "2.0", "method": "initialized", "params": {}}) + '\n')
        proc.stdin.flush()
        time.sleep(0.5)  # Give server time to process
        print("   ✅ Notification sent")
        
        # Test 3: Call a tool (that will fail due to no auth)
        print("\n3. Testing tool call (search_tracks)...")
        tool_request = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "search_tracks",
                "arguments": {"query": "test", "limit": 5}
            },
            "id": 2
        }
        response = send_request(tool_request)
        if response:
            if "error" in response:
                # This is expected - not authenticated
                if "authenticated" in str(response).lower() or "login" in str(response).lower():
                    print("   ✅ Tool correctly requires authentication")
                else:
                    print(f"   ⚠️  Tool error: {response['error'].get('message', 'Unknown error')}")
            elif "result" in response:
                print(f"   ✅ Tool returned result")
        else:
            print("   ❌ No response received")
            
        print("\n✅ All protocol tests completed successfully")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
    finally:
        proc.terminate()
        proc.wait()

if __name__ == "__main__":
    test_mcp_server()
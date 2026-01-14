#!/usr/bin/env python3
"""Test that the MCP server responds to protocol messages."""

import subprocess
import json
import sys

def test_mcp_server():
    """Test MCP server initialization."""
    print("Testing MCP server protocol communication...")

    # Start the server process
    proc = subprocess.Popen(
        ["jupyters-server"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    # Send initialize request
    init_request = {
        "jsonrpc": "2.0",
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {
                "name": "test-client",
                "version": "1.0.0"
            }
        },
        "id": 1
    }

    print(f"Sending: {json.dumps(init_request)}")
    proc.stdin.write(json.dumps(init_request) + "\n")
    proc.stdin.flush()

    # Read response (with timeout)
    import select
    ready = select.select([proc.stdout], [], [], 5)

    if ready[0]:
        response = proc.stdout.readline()
        print(f"Received: {response}")

        try:
            data = json.loads(response)
            if "result" in data:
                print("✓ Server responded with valid MCP initialize response")
                print(f"  Server capabilities: {data['result'].get('capabilities', {})}")

                # List tools
                tools_request = {
                    "jsonrpc": "2.0",
                    "method": "tools/list",
                    "params": {},
                    "id": 2
                }
                proc.stdin.write(json.dumps(tools_request) + "\n")
                proc.stdin.flush()

                ready = select.select([proc.stdout], [], [], 5)
                if ready[0]:
                    tools_response = proc.stdout.readline()
                    tools_data = json.loads(tools_response)
                    if "result" in tools_data:
                        tools = tools_data["result"].get("tools", [])
                        print(f"✓ Server reported {len(tools)} tools")
                        print("  Available tools:")
                        for tool in tools[:10]:  # Show first 10
                            print(f"    - {tool['name']}: {tool.get('description', 'No description')[:60]}")
                        if len(tools) > 10:
                            print(f"    ... and {len(tools) - 10} more")
                        return True
            else:
                print(f"✗ Unexpected response: {data}")
                return False
        except json.JSONDecodeError as e:
            print(f"✗ Failed to parse response: {e}")
            return False
    else:
        print("✗ Server did not respond within timeout")
        stderr = proc.stderr.read()
        if stderr:
            print(f"  stderr: {stderr}")
        return False

    proc.terminate()
    return False

if __name__ == "__main__":
    success = test_mcp_server()
    sys.exit(0 if success else 1)

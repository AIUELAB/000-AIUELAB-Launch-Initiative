#!/usr/bin/env python3
"""
Direct test of native MCP server binary
"""

import json
import os
import subprocess

from dotenv import load_dotenv

load_dotenv()

# Set environment variable
env = os.environ.copy()
env["GITHUB_PERSONAL_ACCESS_TOKEN"] = os.getenv("GITHUB_PAT")

# Start the MCP server
process = subprocess.Popen(
    ["./bin/github-mcp-server", "stdio"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
    env=env,
)

# Send initialize request
initialize_request = {
    "jsonrpc": "2.0",
    "method": "initialize",
    "params": {
        "protocolVersion": "0.1.0",
        "capabilities": {},
        "clientInfo": {"name": "test-client", "version": "1.0.0"},
    },
    "id": 1,
}

process.stdin.write(json.dumps(initialize_request) + "\n")
process.stdin.flush()

# Read response
response = process.stdout.readline()
print("Initialize response:", response)

# Send tools/list request
tools_request = {"jsonrpc": "2.0", "method": "tools/list", "params": {}, "id": 2}

process.stdin.write(json.dumps(tools_request) + "\n")
process.stdin.flush()

# Read response
response = process.stdout.readline()
tools_response = json.loads(response)
print(f"Found {len(tools_response.get('result', {}).get('tools', []))} tools")

# Test a simple call
test_request = {
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {"name": "get_me", "arguments": {}},
    "id": 3,
}

process.stdin.write(json.dumps(test_request) + "\n")
process.stdin.flush()

response = process.stdout.readline()
print(
    "get_me response:",
    json.loads(response).get("result", {}).get("content", [])[0].get("text", "")[:200],
)

process.terminate()

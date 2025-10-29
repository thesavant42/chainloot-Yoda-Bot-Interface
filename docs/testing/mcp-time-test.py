# Make MCP Tools request
import asyncio
import subprocess
import json

async def test_time_tool():
    proc = subprocess.Popen(['uvx', 'mcp-server-time'], 
                           stdin=subprocess.PIPE, 
                           stdout=subprocess.PIPE, 
                           stderr=subprocess.PIPE,
                           text=True)
    
    # Initialize
    init_req = {'jsonrpc': '2.0', 'id': 1, 'method': 'initialize', 'params': {'protocolVersion': '2025-06-18', 'capabilities': {}, 'clientInfo': {'name': 'test-client', 'version': '1.0'}}}
    proc.stdin.write(json.dumps(init_req) + '\n')
    proc.stdin.flush()
    proc.stdout.readline()  # consume init response
    
    # Call the tool for Los Angeles time
    tool_call = {
        'jsonrpc': '2.0', 
        'id': 3, 
        'method': 'tools/call',
        'params': {
            'name': 'get_current_time',
            'arguments': {'timezone': 'America/Los_Angeles'}
        }
    }
    proc.stdin.write(json.dumps(tool_call) + '\n')
    proc.stdin.flush()
    
    # Read response
    response = proc.stdout.readline()
    print(f'Time tool response: {response.strip()}')
    
    proc.terminate()

asyncio.run(test_time_tool())

# Sample Response:

# Time tool response: {"jsonrpc":"2.0","id":3,"result":{"content":[{"type":"text","text":"{\n  \"timezone\": \"America/Los_Angeles\",\n  \"datetime\": \"2025-10-29T09:28:43-07:00\",\n  \"day_of_week\": \"Wednesday\",\n  \"is_dst\": true\n}"}],"isError":false}}Wednesday\",\n  \"is_dst\": true\n}"}],"isError":false}}
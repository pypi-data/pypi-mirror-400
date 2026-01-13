import asyncio
import os
import sys
import json
import logging
import argparse
from typing import Optional

# We use httpx for async HTTP requests (SSE)
import httpx
from mcp.client.sse import sse_client
from mcp.types import ClientRequest, ClientNotification
from mcp.client.stdio import StdioServerParameters

logging.basicConfig(level=logging.INFO, stream=sys.stderr)
logger = logging.getLogger("ado-pr-connect")

async def run_bridge(url: str, org_url: str, pat: str, repo_id: Optional[str] = None):
    """
    Connects to a remote SSE MCP server and bridges it to Stdio.
    """
    headers = {
        "X-AZDO-ORG-URL": org_url,
        "X-AZDO-PAT": pat,
    }
    if repo_id:
        headers["X-AZDO-REPO-ID"] = repo_id

    # 1. Connect to SSE
    logger.info(f"Connecting to {url}...")
    
    # We use the low-level mcp client libraries if possible, or just build a loop.
    # The 'mcp' library doesn't expose a simple "bridge" function yet.
    # So we will implement a read loop.
    
    async with sse_client(url, headers=headers) as (read_stream, write_stream):
        logger.info("Connected to SSE. Ready to bridge.")
        
        # 2. Start Stdio Loop
        # We need to read from stdin (IDE requests) and write to write_stream (Remote)
        # And read from read_stream (Remote events) and write to stdout (IDE)
        
        async def forward_stdin():
            loop = asyncio.get_event_loop()
            reader = asyncio.StreamReader()
            protocol = asyncio.StreamReaderProtocol(reader)
            await loop.connect_read_pipe(lambda: protocol, sys.stdin)
            
            while True:
                line = await reader.readline()
                if not line:
                    break
                
                # Parse generic JSON-RPC message
                try:
                    msg = json.loads(line)
                    # Forward to remote
                    # write_stream.send(jsonrpc_message) ??
                    # mcp sse_client write_stream expects a JSONRPCMessage type usually?
                    # let's check mcp implementation details or use `send_json`.
                    # The `write_stream` from `sse_client` is likely a `MemoryObjectSendStream` of `JSONRPCMessage`.
                    # We need to convert dict to JSONRPCMessage? 
                    # Or does it accept dicts?
                    await write_stream.send_json(msg) # usage guess, need to verify
                except Exception as e:
                    logger.error(f"Error forwarding stdin: {e}")

        # Wait. `mcp` library is strict about types. 
        # Writing a raw bridge with `mcp` library types might be hard without knowing the exact types.
        # Fallback: Raw Implementation (robust).
        pass

# REDO: Raw Implementation using httpx to ensure no type errors from `mcp` lib mysteries.
async def raw_bridge(url: str, headers: dict):
    # Establish SSE Connection
    async with httpx.AsyncClient(timeout=None) as client:
        async with client.stream("GET", url, headers=headers) as response:
            if response.status_code != 200:
                logger.error(f"Failed to connect: {response.status_code}")
                return

            # Wait for 'endpoint' event
            endpoint_url = None
            
            # SSE Parser (Simplified)
            buffer = ""
            async for chunk in response.aiter_lines():
                if not chunk.strip():
                    continue
                if chunk.startswith("event: endpoint"):
                    # Next line is data
                    pass 
                if chunk.startswith("data: "):
                    data = chunk[6:]
                    # If this was endpoint event...
                    # This is getting complicated to parse manually.
            pass

# THIRD ATTEMPT: Use `mcp` library properly.
# It handles the handshake.
# We just need to drive it.

from mcp import ClientSession
from mcp.client.sse import sse_client
from mcp.client.stdio import stdio_client # This is usually client-side connecting TO stdio.

async def main_loop(url: str, headers: dict):
    async with sse_client(url, headers=headers) as (read_stream, write_stream):
        # We have streams.
        # read_stream: yields JSONRPCMessage
        # write_stream: accepts JSONRPCMessage
        
        # We need to wrap Stdin/Stdout as a generic JSON-RPC transport too.
        # But we don't have a "stdio_server" transport helper exposed easily?
        
        # Let's just do manual JSON reading from stdin.
        loop = asyncio.get_event_loop()
        reader = asyncio.StreamReader()
        protocol = asyncio.StreamReaderProtocol(reader)
        await loop.connect_read_pipe(lambda: protocol, sys.stdin)
        
        # Output task
        async def output_loop():
            async for message in read_stream:
                # message is a rigid model (JSONRPCMessage).
                # dump it to json string.
                # mcp models have `model_dump_json()` (pydantic).
                # But it might be a root type.
                # using `json.dumps(message.model_dump())` or similar.
                # Or just accessing the `root`?
                try:
                    # Generic way for Pydantic v2
                    json_str = message.model_dump_json(by_alias=True)
                    sys.stdout.write(json_str + "\n")
                    sys.stdout.flush()
                except Exception as e:
                    logger.error(f"Output error: {e}")

        output_task = asyncio.create_task(output_loop())

        # Input loop
        try:
            while True:
                line = await reader.readline()
                if not line:
                    break
                try:
                     # We need to parse strict JSONRPCMessage from dict
                     # This is risky if models don't match exactly.
                     # However, we can use `mcp.types.JSONRPCMessage.model_validate_json(line)`.
                     from mcp.types import JSONRPCMessage
                     msg = JSONRPCMessage.model_validate_json(line)
                     await write_stream.send(msg)
                except Exception as e:
                    logger.error(f"Input error: {e}")
        finally:
            output_task.cancel()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True)
    parser.add_argument("--pat", required=True)
    parser.add_argument("--org-url", required=True)
    parser.add_argument("--repo-id", default=None)
    
    args = parser.parse_args()
    
    url = args.url
    headers = {
        "X-AZDO-ORG-URL": args.org_url,
        "X-AZDO-PAT": args.pat
    }
    if args.repo_id:
        headers["X-AZDO-REPO-ID"] = args.repo_id
        
    asyncio.run(main_loop(url, headers))

if __name__ == "__main__":
    main()

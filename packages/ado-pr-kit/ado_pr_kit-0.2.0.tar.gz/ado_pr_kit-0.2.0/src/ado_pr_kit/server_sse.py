from .server import mcp

# Expose the ASGI app for uvicorn
# Usage: uvicorn ado_pr_kit.server_sse:app --host 0.0.0.0 --port 8000
app = mcp.sse_app

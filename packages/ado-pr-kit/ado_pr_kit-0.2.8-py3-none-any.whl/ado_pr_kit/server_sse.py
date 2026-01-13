"""
SSE Server Entry Point with Header-Based Authentication

This module provides an ASGI app that accepts Azure DevOps credentials via HTTP headers,
allowing remote MCP clients to configure credentials securely at connection time.

Usage:
    uvicorn ado_pr_kit.server_sse:app --host 0.0.0.0 --port 8000

Connect with credentials in headers:
    X-AZDO-ORG-URL: https://dev.azure.com/myorg
    X-AZDO-PAT: your-personal-access-token
    X-AZDO-PROJECT: your-project (optional)
    X-AZDO-REPO-ID: your-repo-id (optional)
"""

from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route
from starlette.types import ASGIApp, Receive, Scope, Send
from .server import mcp
from .config import Settings, _settings_ctx


class CredentialMiddleware:
    """
    Pure ASGI middleware that extracts Azure DevOps credentials from HTTP headers
    and injects them into the settings context. Compatible with SSE streaming.
    """
    
    def __init__(self, app: ASGIApp):
        self.app = app
    
    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        # Extract headers from scope
        headers = dict(scope.get("headers", []))
        
        # Build overrides from headers (headers are bytes)
        overrides = {}
        if headers.get(b'x-azdo-org-url'):
            overrides['AZDO_ORG_URL'] = headers[b'x-azdo-org-url'].decode()
        if headers.get(b'x-azdo-pat'):
            overrides['AZDO_PAT'] = headers[b'x-azdo-pat'].decode()
        if headers.get(b'x-azdo-project'):
            overrides['AZDO_PROJECT'] = headers[b'x-azdo-project'].decode()
        if headers.get(b'x-azdo-repo-id'):
            overrides['AZDO_REPO_ID'] = headers[b'x-azdo-repo-id'].decode()
        
        # Create settings with overrides
        new_settings = Settings(**overrides)
        
        # Set context var for this request
        token = _settings_ctx.set(new_settings)
        
        try:
            await self.app(scope, receive, send)
        finally:
            _settings_ctx.reset(token)


async def health_check(request):
    """Health check endpoint."""
    return JSONResponse({
        "status": "ok",
        "service": "AdoPRKit MCP Server",
        "version": "0.2.8",
        "description": "MCP server for managing Azure DevOps Pull Requests",
        "endpoints": {
            "sse": "/sse",
            "messages": "/messages"
        },
        "headers": {
            "X-AZDO-ORG-URL": "Your Azure DevOps org URL (required)",
            "X-AZDO-PAT": "Your Personal Access Token (required)",
            "X-AZDO-PROJECT": "Your Azure DevOps project name (required)",
            "X-AZDO-REPO-ID": "Default repository ID (required)"
        },
        "note": "REPO-ID sets your default repo. You can query any repo by passing repository_id to tools."
    })


# Create the main Starlette app with health check route
routes = [
    Route("/", health_check),
]

# Get the MCP SSE app
sse_app = mcp.sse_app()

# Create wrapper app
wrapper_app = Starlette(routes=routes)

# Mount the SSE app
wrapper_app.mount("/", sse_app)

# Wrap with credential middleware
app = CredentialMiddleware(wrapper_app)

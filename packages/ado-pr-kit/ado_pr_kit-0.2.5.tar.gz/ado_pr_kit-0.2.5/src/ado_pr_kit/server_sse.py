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

from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware
from .server import mcp
from .config import Settings, _settings_ctx


# Create a FastAPI wrapper app
wrapper_app = FastAPI(title="AdoPRKit MCP Server")


class CredentialMiddleware(BaseHTTPMiddleware):
    """
    Middleware that extracts Azure DevOps credentials from HTTP headers
    and injects them into the settings context for the duration of the request.
    """
    
    async def dispatch(self, request: Request, call_next):
        # Create a new Settings object, initially based on defaults (env vars)
        # We can't easily "clone" the existing default one if it's not exposed, 
        # so we instantiate a new one (loading env vars) and override.
        # This is safe because Settings() loads from os.environ by default.
        
        # Override values from headers if present
        overrides = {}
        if request.headers.get('x-azdo-org-url'):
            overrides['AZDO_ORG_URL'] = request.headers.get('x-azdo-org-url')
        if request.headers.get('x-azdo-pat'):
            overrides['AZDO_PAT'] = request.headers.get('x-azdo-pat')
        if request.headers.get('x-azdo-project'):
            overrides['AZDO_PROJECT'] = request.headers.get('x-azdo-project')
        if request.headers.get('x-azdo-repo-id'):
            overrides['AZDO_REPO_ID'] = request.headers.get('x-azdo-repo-id')
        
        # Instantiate new settings with overrides
        # We can pass overrides to constructor if we want, or set them after.
        # Pydantic Settings allows init with kwargs to override env vars.
        new_settings = Settings(**overrides)

        # Set the context var for this request
        token = _settings_ctx.set(new_settings)
        
        try:
            # Process the request
            response = await call_next(request)
            return response
        finally:
            # Reset the context var to previous state
            _settings_ctx.reset(token)


# Add the credential middleware
wrapper_app.add_middleware(CredentialMiddleware)


@wrapper_app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "ok",
        "service": "AdoPRKit MCP Server",
        "version": "0.2.5",
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
    }


# Mount the actual MCP SSE routes
wrapper_app.mount("/", mcp.sse_app)

# Export the wrapper app as the main ASGI app
app = wrapper_app

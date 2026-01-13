"""
SSE Server Entry Point with Query Parameter Authentication

This module provides an ASGI app that accepts Azure DevOps credentials via URL query parameters,
allowing remote MCP clients to configure credentials at connection time.

Usage:
    uvicorn ado_pr_kit.server_sse:app --host 0.0.0.0 --port 8000

Connect with credentials in URL:
    https://your-server.com/sse?azdo_org_url=https://dev.azure.com/myorg&azdo_pat=TOKEN&azdo_repo_id=repo
"""

from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware
from urllib.parse import parse_qs, urlparse
from .server import mcp
from .config import settings

# Create a FastAPI wrapper app
wrapper_app = FastAPI(title="AdoPRKit MCP Server")


class CredentialMiddleware(BaseHTTPMiddleware):
    """
    Middleware that extracts Azure DevOps credentials from query parameters
    and injects them into the settings for the duration of the request.
    """
    
    async def dispatch(self, request: Request, call_next):
        # Extract query parameters
        query_params = dict(request.query_params)
        
        # Store original settings values
        original_org_url = settings.AZDO_ORG_URL
        original_pat = settings.AZDO_PAT
        original_project = settings.AZDO_PROJECT
        original_repo_id = settings.AZDO_REPO_ID
        
        try:
            # Override settings with query params if provided
            if 'azdo_org_url' in query_params:
                settings.AZDO_ORG_URL = query_params['azdo_org_url']
            if 'azdo_pat' in query_params:
                settings.AZDO_PAT = query_params['azdo_pat']
            if 'azdo_project' in query_params:
                settings.AZDO_PROJECT = query_params['azdo_project']
            if 'azdo_repo_id' in query_params:
                settings.AZDO_REPO_ID = query_params['azdo_repo_id']
            
            # Process the request
            response = await call_next(request)
            return response
        finally:
            # Restore original settings (for other concurrent requests)
            settings.AZDO_ORG_URL = original_org_url
            settings.AZDO_PAT = original_pat
            settings.AZDO_PROJECT = original_project
            settings.AZDO_REPO_ID = original_repo_id


# Add the credential middleware
wrapper_app.add_middleware(CredentialMiddleware)


# Mount the MCP SSE app under the wrapper
@wrapper_app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "ok",
        "service": "AdoPRKit MCP Server",
        "version": "0.2.1",
        "endpoints": {
            "sse": "/sse",
            "messages": "/messages"
        },
        "usage": "Connect to /sse with query params: ?azdo_org_url=...&azdo_pat=...&azdo_repo_id=..."
    }


# Mount the actual MCP SSE routes
# The mcp.sse_app handles /sse and /messages endpoints
wrapper_app.mount("/", mcp.sse_app)


# Export the wrapper app as the main ASGI app
app = wrapper_app

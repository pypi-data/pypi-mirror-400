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
from .config import settings

# Create a FastAPI wrapper app
wrapper_app = FastAPI(title="AdoPRKit MCP Server")


class CredentialMiddleware(BaseHTTPMiddleware):
    """
    Middleware that extracts Azure DevOps credentials from HTTP headers
    and injects them into the settings for the duration of the request.
    """
    
    async def dispatch(self, request: Request, call_next):
        # Store original settings values
        original_org_url = settings.AZDO_ORG_URL
        original_pat = settings.AZDO_PAT
        original_project = settings.AZDO_PROJECT
        original_repo_id = settings.AZDO_REPO_ID
        
        try:
            # Override settings with headers if provided
            if request.headers.get('x-azdo-org-url'):
                settings.AZDO_ORG_URL = request.headers.get('x-azdo-org-url')
            if request.headers.get('x-azdo-pat'):
                settings.AZDO_PAT = request.headers.get('x-azdo-pat')
            if request.headers.get('x-azdo-project'):
                settings.AZDO_PROJECT = request.headers.get('x-azdo-project')
            if request.headers.get('x-azdo-repo-id'):
                settings.AZDO_REPO_ID = request.headers.get('x-azdo-repo-id')
            
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


@wrapper_app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "ok",
        "service": "AdoPRKit MCP Server",
        "version": "0.2.2",
        "endpoints": {
            "sse": "/sse",
            "messages": "/messages"
        },
        "headers": {
            "X-AZDO-ORG-URL": "Your Azure DevOps org URL (required)",
            "X-AZDO-PAT": "Your Personal Access Token (required)",
            "X-AZDO-PROJECT": "Default project name (optional)",
            "X-AZDO-REPO-ID": "Default repository ID (optional)"
        }
    }


# Mount the actual MCP SSE routes
wrapper_app.mount("/", mcp.sse_app)

# Export the wrapper app as the main ASGI app
app = wrapper_app

# Use a Python image with uv pre-installed
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

# Install the project into `/app`
WORKDIR /app
COPY . .
RUN uv sync --frozen --no-cache

# Place the virtualenv in the path
ENV PATH="/app/.venv/bin:$PATH"

# Run the MCP server using uvicorn (SSE mode)
# Default port is 8000
CMD ["uvicorn", "ado_pr_kit.server_sse:app", "--host", "0.0.0.0", "--port", "8000"]

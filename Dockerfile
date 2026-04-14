FROM python:3.12-slim

# Pre-install mcp-memory-service so container starts instantly
RUN pip install --no-cache-dir mcp-memory-service

# Create data directories
RUN mkdir -p /data/memory /data/backups

WORKDIR /app

ENV MCP_MEMORY_CHROMA_PATH=/data/memory \
    MCP_MEMORY_BACKUPS_PATH=/data/backups \
    MCP_SSE_HOST=0.0.0.0 \
    MCP_SSE_PORT=8765 \
    MCP_STREAMABLE_HTTP_MODE=1 \
    MCP_OAUTH_ENABLED=false

EXPOSE 8765

CMD ["python", "-m", "mcp_memory_service.server"]

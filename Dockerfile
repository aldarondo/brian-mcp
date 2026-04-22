FROM python:3.12-slim

# Install torch CPU-only + mcp-memory-service in one pip call.
# --index-url forces torch to resolve from the CPU wheel index;
# --extra-index-url supplies PyPI for everything else.
RUN pip install --no-cache-dir \
    --index-url https://download.pytorch.org/whl/cpu \
    --extra-index-url https://pypi.org/simple/ \
    torch mcp-memory-service

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

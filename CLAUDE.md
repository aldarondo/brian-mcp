# brian-mcp

## Project Purpose
Self-hosted MCP memory server on Synology NAS Docker, exposed via Cloudflare Tunnel for remote access from Claude Code sessions.

## Key Commands
```bash
# Start the stack (run on Synology via SSH)
docker compose up -d

# View logs
docker compose logs -f mcp-memory

# Restart a container
docker compose restart mcp-memory

# Run tests
pytest tests/
```

## Deployment Target
- **Host:** Synology NAS (SSH: `charles@synology`)
- **Storage:** `/volume1/docker/brian-mcp/`
- **Port:** 8765 (internal), exposed via Cloudflare Tunnel
- **Tunnel URL:** `https://brian.[domain].com/memory` (fill in once configured)

## Testing Requirements (mandatory)
- Every feature or bug fix must include unit tests covering the core logic
- Every user-facing flow must have at least one integration test
- Tests live in `tests/unit/` and `tests/integration/`
- Run all tests before marking any task complete: `pytest tests/`

@~/Documents/GitHub/CLAUDE.md

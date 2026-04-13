# brian-mcp

## What This Project Is
Shared MCP memory server for the Aldarondo family — provides a persistent, always-on knowledge source that Claude skills can read and write across all family members. Runs on Synology NAS via Docker, exposed publicly at `https://brian.aldarondo.us/memory` via Cloudflare Tunnel.

## Tech Stack
- **Memory service:** `mcp-memory-service` (Python, ChromaDB vector store)
- **Container runtime:** Synology Container Manager (Docker Compose)
- **Storage:** `/volume1/docker/brian-mcp/` on Synology NAS
- **Tunnel:** Cloudflare Tunnel (`cloudflared`) — domain: `aldarondo.us`
- **Endpoint:** `https://brian.aldarondo.us/memory`

## Key Decisions
- Family members are scoped via tags: `user:charles`, `user:*` for shared memories
- No custom wrapper code over `mcp-memory-service` — use it as-is
- `cloudflared` runs as a second container in the same Compose stack (token mode via `TUNNEL_TOKEN` env var)
- Cloudflare account is ready; domain is `aldarondo.us`

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

## Session Startup Checklist
1. SSH into Synology: `ssh charles@synology`
2. Check containers: `docker compose ps` from `/volume1/docker/brian-mcp/`
3. Check tunnel is live: `curl https://brian.aldarondo.us/memory/health`

## Testing Requirements (mandatory)
- Every feature or bug fix must include unit tests covering the core logic
- Every user-facing flow must have at least one integration test
- Tests live in `tests/unit/` and `tests/integration/`
- Run all tests before marking any task complete: `pytest tests/`
- Set `MCP_MEMORY_URL=http://localhost:8765` for integration tests

@~/Documents/GitHub/CLAUDE.md

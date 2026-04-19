# brian-mcp

## What This Project Is
Shared MCP memory server for the Aldarondo family — provides a persistent, always-on knowledge source that Claude skills can read and write across all family members. Runs on Synology NAS via Docker, exposed publicly at `https://brian.aldarondo.family/mcp` via Cloudflare Tunnel with Access authentication.

## Tech Stack
- **Memory service:** `mcp-memory-service` (Python, ChromaDB vector store)
- **Container image:** `ghcr.io/aldarondo/brian-mcp-memory:latest` (CPU-only torch, ~2GB)
- **Container runtime:** Synology Container Manager (Docker Compose)
- **Storage:** `/volume1/docker/brian-mcp/` on Synology NAS
- **Tunnel:** Cloudflare Tunnel (`cloudflared`) — domain: `aldarondo.family`
- **Auth:** Cloudflare Access — OTP email for family, service token for Claude Code
- **Endpoint:** `https://brian.aldarondo.family/mcp`

## Key Decisions
- Family members are scoped via tags: `user:charles`, `user:*` for shared memories
- No custom wrapper code over `mcp-memory-service` — use it as-is
- `cloudflared` runs as a second container in the same Compose stack (token mode via `TUNNEL_TOKEN` env var)
- Cloudflare Access service token credentials stored in `.env` as `CF_ACCESS_CLIENT_ID` / `CF_ACCESS_CLIENT_SECRET`

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
3. Health check (LAN): `curl http://192-168-0-64.aldarondo.direct.quickconnect.to:8765/health`
4. Health check (public): `curl -X POST https://brian.aldarondo.family/mcp -H "Content-Type: application/json" -d '{"jsonrpc":"2.0","method":"ping","id":1}'`

## Deployment Phases
- **Phase 1 (complete):** LAN — `http://192-168-0-64.aldarondo.direct.quickconnect.to:8765`
- **Phase 2 (complete):** Public — `https://brian.aldarondo.family/mcp` via Cloudflare Tunnel ✅
- **Phase 3 (complete):** Cloudflare Access auth — OTP for family, service token for Claude Code ✅

## Testing Requirements (mandatory)
- Every feature or bug fix must include unit tests covering the core logic
- Every user-facing flow must have at least one integration test
- Tests live in `tests/unit/` and `tests/integration/`
- Run all tests before marking any task complete: `pytest tests/`
- Integration tests run against the live endpoint: `MCP_MEMORY_URL=https://brian.aldarondo.family/mcp pytest tests/integration/`

@~/Documents/GitHub/CLAUDE.md

## Git Rules
- Never create pull requests. Push directly to main.
- solo/auto-push OK

# brian-mcp

Self-hosted MCP memory server running on Synology NAS via Docker, exposed publicly at `https://brian.aldarondo.family/mcp` via Cloudflare Tunnel with Access authentication.

## Features
- Persistent vector memory via `mcp-memory-service` (ChromaDB backend)
- Remote MCP endpoint over HTTP/SSE — reachable from any Claude Code session
- Multi-user tagging (`user:charles`, `user:*`) for scoped memory retrieval
- Always-on: Container Manager restart policy + Cloudflare Tunnel keep-alive
- Cloudflare Access: OTP email policy for family members, service token for Claude Code

## Tech Stack
| Layer | Technology |
|---|---|
| Memory service | `mcp-memory-service` (Python, ChromaDB) |
| Container image | `ghcr.io/aldarondo/brian-mcp-memory:latest` (CPU-only torch, ~2GB) |
| Container runtime | Synology Container Manager (Docker) |
| Storage | Synology volume (`/volume1/docker/brian-mcp/`) |
| Tunnel | Cloudflare Tunnel (`cloudflared`) |
| Auth | Cloudflare Access — OTP email for family, service token for Claude Code |
| Orchestration | Docker Compose |

## Getting Started

### Prerequisites
- Synology NAS with Container Manager installed
- Cloudflare account with tunnel token and Access service token
- SSH access to the NAS (`charles@synology`)
- NAS authenticated to ghcr.io (`docker login ghcr.io`)

### Deploy

```bash
# SSH into Synology
ssh charles@synology

# Clone repo to NAS
git clone https://github.com/aldarondo/brian-mcp /volume1/docker/brian-mcp

# Copy and fill in secrets
cp .env.example .env
nano .env

# Pull image and start stack
cd /volume1/docker/brian-mcp
docker compose pull
docker compose up -d
```

### Environment Variables (`.env`)

```env
MCP_MEMORY_CHROMA_PATH=/data/memory
MCP_MEMORY_BACKUPS_PATH=/data/backups
MCP_SSE_HOST=0.0.0.0
MCP_SSE_PORT=8765
MCP_STREAMABLE_HTTP_MODE=1
MCP_OAUTH_ENABLED=false
TUNNEL_TOKEN=<cloudflare-tunnel-token>
CF_ACCESS_CLIENT_ID=<service-token-client-id>
CF_ACCESS_CLIENT_SECRET=<service-token-client-secret>
```

### Validate

```bash
# Health check via tunnel (requires CF Access service token headers)
curl https://brian.aldarondo.family/mcp \
  -H "CF-Access-Client-Id: $CF_ACCESS_CLIENT_ID" \
  -H "CF-Access-Client-Secret: $CF_ACCESS_CLIENT_SECRET"

# Run integration tests
MCP_MEMORY_URL=https://brian.aldarondo.family/mcp pytest tests/integration/
```

### Connect to Claude Code

Add to your MCP config:
```json
{
  "brian-memory": {
    "type": "http",
    "url": "https://brian.aldarondo.family/mcp",
    "headers": {
      "CF-Access-Client-Id": "<service-token-client-id>",
      "CF-Access-Client-Secret": "<service-token-client-secret>"
    }
  }
}
```

## Maintenance
- **Rebuild image:** when `mcp-memory-service` releases an update, rebuild and push `ghcr.io/aldarondo/brian-mcp-memory:latest`, then `docker compose pull && docker compose up -d` on the NAS.
- **Re-auth NAS:** if the GitHub PAT expires, generate a new `write:packages` PAT and run `docker login ghcr.io` on the NAS.
- **Cloudflare Access:** service token lives in `.env`; family OTP policy covers `charles.aldarondo@gmail.com` and the other family addresses configured in Cloudflare Zero Trust.

## Project Status
**Production / maintenance mode.** All three phases complete:
- Phase 1: LAN endpoint on port 8765 ✅
- Phase 2: Public endpoint via Cloudflare Tunnel ✅
- Phase 3: Cloudflare Access authentication ✅

See [ROADMAP.md](ROADMAP.md) for full history.

---
**Publisher:** Xity Software, LLC

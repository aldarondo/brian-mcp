# brian-mcp

Self-hosted MCP memory server running on Synology NAS via Docker, exposed to the internet through a Cloudflare Tunnel.

## Features
- Persistent vector memory via `mcp-memory-service` (ChromaDB backend)
- Remote MCP endpoint over HTTP/SSE — reachable from any Claude Code session
- Multi-user tagging (`user:charles`, `user:*`) for scoped memory retrieval
- Always-on: Container Manager restart policy + Cloudflare Tunnel keep-alive

## Tech Stack
| Layer | Technology |
|---|---|
| Memory service | `mcp-memory-service` (Python, ChromaDB) |
| Container runtime | Synology Container Manager (Docker) |
| Storage | Synology volume (`/volume1/docker/brian-mcp/`) |
| Tunnel | Cloudflare Tunnel (`cloudflared`) |
| Orchestration | Docker Compose |

## Getting Started

### Prerequisites
- Synology NAS with Container Manager installed
- Cloudflare account with a domain and tunnel token
- SSH access to the NAS

### Deploy

```bash
# SSH into Synology
ssh charles@synology

# Clone repo to NAS
git clone https://github.com/[your-org]/brian-mcp /volume1/docker/brian-mcp

# Copy and fill in secrets
cp .env.example .env
nano .env

# Start stack
cd /volume1/docker/brian-mcp
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
TUNNEL_TOKEN=<your-cloudflare-tunnel-token>
```

### Validate

```bash
# Health check (from inside NAS or tunnel URL)
curl https://brian.[your-domain].com/memory/health

# Add a memory
curl -X POST https://brian.[your-domain].com/memory/add \
  -H "Content-Type: application/json" \
  -d '{"content": "test memory", "tags": ["user:charles"]}'

# Search memories
curl -X POST https://brian.[your-domain].com/memory/search \
  -H "Content-Type: application/json" \
  -d '{"query": "test", "tags": ["user:charles"]}'
```

## Project Status
Early development. See [ROADMAP.md](ROADMAP.md) for what's planned.

---
**Publisher:** Xity Software, LLC

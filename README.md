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
- Cloudflare account with a tunnel token and Access service token (see below)
- SSH access to the NAS (`charles@synology`)
- NAS authenticated to ghcr.io: `docker login ghcr.io` (use a PAT with `write:packages` scope)

### Obtain Required Secrets

**Cloudflare Tunnel token (`TUNNEL_TOKEN`):**
1. Cloudflare Dashboard → Zero Trust → Networks → Tunnels
2. Select your tunnel → Configure → Install connector
3. Copy the token from the `--token` argument shown in the install command

**Cloudflare Access Service Token (`CF_ACCESS_CLIENT_ID` / `CF_ACCESS_CLIENT_SECRET`):**
1. Cloudflare Dashboard → Zero Trust → Access → Service Auth
2. Click "Create Service Token" — name it `brian-mcp-claude-code`
3. Copy both the Client ID (ends in `.access`) and Client Secret immediately — the secret is only shown once

### Deploy

```bash
# SSH into Synology
ssh charles@synology

# Clone repo to NAS
git clone https://github.com/aldarondo/brian-mcp /volume1/docker/brian-mcp
cd /volume1/docker/brian-mcp

# Copy and fill in secrets
cp .env.example .env
nano .env   # Fill in TUNNEL_TOKEN, CF_ACCESS_CLIENT_ID, CF_ACCESS_CLIENT_SECRET

# Pull image and start stack (include tunnel profile to start cloudflared)
docker compose pull
docker compose --profile tunnel up -d
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
CF_ACCESS_CLIENT_ID=<service-token-client-id>.access
CF_ACCESS_CLIENT_SECRET=<service-token-client-secret>
```

### Post-Deployment Checklist

After deploying, verify each of these before declaring the stack healthy:

```bash
# 1. Both containers running
docker compose ps
# Expected: brian-mcp-memory (healthy), brian-mcp-tunnel (running)

# 2. LAN health check (no auth required)
curl -s -X POST http://localhost:8765/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"ping","id":1}'
# Expected: 200 response

# 3. Public endpoint via tunnel (requires service token)
curl -s -X POST https://brian.aldarondo.family/mcp \
  -H "Content-Type: application/json" \
  -H "CF-Access-Client-Id: $CF_ACCESS_CLIENT_ID" \
  -H "CF-Access-Client-Secret: $CF_ACCESS_CLIENT_SECRET" \
  -d '{"jsonrpc":"2.0","method":"ping","id":1}'
# Expected: 200 response

# 4. Run integration tests
source .env.test && pytest tests/integration/ -v
# Expected: all tests pass
```

### Connect to Claude Code

Add to your MCP config:
```json
{
  "brian-memory": {
    "type": "http",
    "url": "https://brian.aldarondo.family/mcp",
    "headers": {
      "CF-Access-Client-Id": "<service-token-client-id>.access",
      "CF-Access-Client-Secret": "<service-token-client-secret>"
    }
  }
}
```

## Maintenance

### Logs
Both containers use the `json-file` driver with automatic rotation (5 × 10MB per service). Logs persist across container restarts and recreates — only `docker rm` clears them.

```bash
# Stream live logs
docker logs -f brian-mcp-memory
docker logs -f brian-mcp-tunnel

# Last 100 lines
docker logs --tail 100 brian-mcp-memory
```

### Backups

The ChromaDB store lives at `/volume1/docker/brian-mcp/memory` (host bind mount); container recreation does not touch it. Snapshots and an append-only `backup.log` go to `/volume1/docker/brian-mcp/backups/`.

**Daily snapshot (`scripts/backup.sh`):** stops `mcp-memory`, tars `memory/` into `backups/memory-YYYY-MM-DD.tar.gz`, restarts the container, then prunes old snapshots — keeping the last 7 daily plus the newest snapshot in each of the 4 most recent weeks beyond that. Container downtime is ~5 seconds.

Schedule it via Synology **Control Panel → Task Scheduler → Create → Scheduled Task → User-defined script**:
- **General:** user `root`, name `brian-mcp daily backup`
- **Schedule:** Daily, 03:00
- **Run command:** `/volume1/docker/brian-mcp/scripts/backup.sh`

**Restore (`scripts/restore.sh`):**
```bash
ssh charles@synology
cd /volume1/docker/brian-mcp
sudo ./scripts/restore.sh /volume1/docker/brian-mcp/backups/memory-2026-04-25.tar.gz
```
Existing data is moved to `memory.before-restore-<timestamp>` rather than deleted, so you can roll back if the restore looks wrong.

### Other maintenance
- **Rebuild image:** when `mcp-memory-service` releases an update, GitHub Actions builds and pushes a new image automatically on Sunday at 03:00 UTC. Then `docker compose pull && docker compose up -d` on the NAS.
- **Re-auth NAS:** if the GitHub PAT expires, generate a new `write:packages` PAT and run `docker login ghcr.io` on the NAS.
- **Cloudflare Access:** service token lives in `.env`; family OTP policy covers `charles.aldarondo@gmail.com` and the other family addresses configured in Cloudflare Zero Trust.

## Troubleshooting

**Container won't start / stays unhealthy:**
```bash
docker logs brian-mcp-memory        # Check for Python errors
docker inspect brian-mcp-memory     # Check health status details
# Look for "connect_ex=111" in health output — means port 8765 not listening
```

**Cloudflare Access denies connection (403):**
- Verify `CF_ACCESS_CLIENT_ID` and `CF_ACCESS_CLIENT_SECRET` in `.env.test` match the current service token in Cloudflare Zero Trust → Access → Service Auth
- Service tokens expire; check expiration date in the dashboard

**Integration tests timeout:**
```bash
MCP_TEST_TIMEOUT=60 pytest tests/integration/ -v   # Increase timeout
# If still failing, check LAN endpoint directly first:
MCP_MEMORY_URL=http://192-168-0-64.aldarondo.direct.quickconnect.to:8765/mcp pytest tests/integration/ -v
```

**GitHub Actions deploy fails:**
- Check run logs at: https://github.com/aldarondo/brian-mcp/actions
- Common cause: cloudflared SSH proxy command fails. Verify `nas-ssh.aldarondo.family` is still the correct hostname in the Cloudflare Access application config
- Run `cloudflared access ssh --hostname nas-ssh.aldarondo.family` locally to confirm connectivity

**Tunnel disconnected:**
```bash
docker logs brian-mcp-tunnel        # Check for authentication errors
docker compose restart cloudflared  # Restart tunnel
# If TUNNEL_TOKEN expired, generate a new one in Cloudflare Dashboard and update .env
```

## Project Status
**Production / maintenance mode.** All three phases complete:
- Phase 1: LAN endpoint on port 8765 ✅
- Phase 2: Public endpoint via Cloudflare Tunnel ✅
- Phase 3: Cloudflare Access authentication ✅

See [ROADMAP.md](ROADMAP.md) for full history.

---
**Publisher:** Xity Software, LLC

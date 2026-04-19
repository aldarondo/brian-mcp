# brian-mcp Roadmap
> Tag key: `[Code]` = Claude Code · `[Cowork]` = Claude Cowork · `[Human]` = Charles must act

## 🎯 Current Milestone
Validate MCP memory works end-to-end on LAN — store, retrieve, and tag memories from a Claude Code session.

## 🔄 In Progress
<!-- Phase 2 complete — move to Phase 3 hardening when ready -->

## 🔲 Backlog

### Phase 2 — Production Hardening
- [x] `[Human]` Generate GitHub PAT with `write:packages` scope
- [x] `[Code]` Push `ghcr.io/aldarondo/brian-mcp-memory:latest` to GHCR (eliminates 3-5min pip install on restart)
- [x] `[Code]` Update docker-compose.yml on NAS to pull from ghcr.io
- [ ] `[Human]` Create Cloudflare Tunnel in dashboard for `brian.aldarondo.us/memory` → copy tunnel token
- [ ] `[Human]` Add `TUNNEL_TOKEN` to `.env` on Synology, start tunnel: `docker compose --profile tunnel up -d`
- [ ] `[Human]` Validate endpoint reachable externally: `curl https://brian.aldarondo.us/memory/health`
- [ ] `[Human]` Update Remote MCP server URL in Claude Code to `https://brian.aldarondo.us/memory`

### Phase 3 — Test Coverage
- [ ] `[Code]` Write integration tests for add/search/delete flows against live endpoint
- [ ] `[Code]` Write unit tests for any helper utilities

## ✅ Completed
- 2026-04-18 `[Human]` GitHub PAT (`write:packages`) provided — GHCR login on NAS
- 2026-04-18 `[Code]` Fixed Dockerfile: CPU-only torch via single pip call with `--index-url pytorch cpu` — image 1.45GB (was 5.42GB with CUDA)
- 2026-04-18 `[Code]` Pushed `ghcr.io/aldarondo/brian-mcp-memory:latest` to GHCR (digest: sha256:4022fd2f...)
- 2026-04-18 `[Code]` Updated docker-compose.yml on NAS — container restarts in ~10s, no more 3-min pip install
- 2026-04-14 `[Code]` Initial scaffold — docker-compose.yml, .env.example, cloudflared config, tests/
- 2026-04-14 `[Code]` Game plan defined
- 2026-04-14 `[Human]` Deployed stack to Synology — `brian-mcp-memory` running on port 8765
- 2026-04-14 `[Code]` Confirmed MCP endpoint live: `http://192-168-0-64.aldarondo.direct.quickconnect.to:8765/mcp` returns 200
- 2026-04-14 `[Code]` Dockerfile created with CPU-only torch (image built locally, ~2GB)
- 2026-04-14 `[Human]` MCP server added to Claude Code — `brian-memory` connected
- 2026-04-14 `[Code]` Full round-trip validated: store → search (semantic + tag filter) → delete — **Phase 1 complete**
- 2026-04-19 `[Human]` Cloudflare Tunnel created, DNS `brian.aldarondo.family` CNAME set
- 2026-04-19 `[Code]` Ingress rule set via Cloudflare MCP — `brian.aldarondo.family` → `http://mcp-memory:8765`
- 2026-04-19 `[Code]` Tunnel live — `https://brian.aldarondo.family/mcp` returns 200 — **Phase 2 complete**

## 🚫 Blocked
<!-- log blockers here -->

# brian-mcp Roadmap
> Tag key: `[Code]` = Claude Code · `[Cowork]` = Claude Cowork · `[Human]` = Charles must act

## 🎯 Current Milestone
Validate MCP memory works end-to-end on LAN — store, retrieve, and tag memories from a Claude Code session.

## 🔄 In Progress
<!-- nothing active right now —  move to Phase 2 when ready -->

## 🔲 Backlog

### Phase 2 — Production Hardening
- [ ] `[Human]` Generate GitHub PAT with `write:packages` scope
- [ ] `[Code]` Push `ghcr.io/aldarondo/brian-mcp-memory:latest` to GHCR (eliminates 3-5min pip install on restart)
- [ ] `[Code]` Update docker-compose.yml on NAS to pull from ghcr.io
- [ ] `[Human]` Create Cloudflare Tunnel in dashboard for `brian.aldarondo.us/memory` → copy tunnel token
- [ ] `[Human]` Add `TUNNEL_TOKEN` to `.env` on Synology, start tunnel: `docker compose --profile tunnel up -d`
- [ ] `[Human]` Validate endpoint reachable externally: `curl https://brian.aldarondo.us/memory/health`
- [ ] `[Human]` Update Remote MCP server URL in Claude Code to `https://brian.aldarondo.us/memory`

### Phase 3 — Test Coverage
- [ ] `[Code]` Write integration tests for add/search/delete flows against live endpoint
- [ ] `[Code]` Write unit tests for any helper utilities

## ✅ Completed
- 2026-04-14 `[Code]` Initial scaffold — docker-compose.yml, .env.example, cloudflared config, tests/
- 2026-04-14 `[Code]` Game plan defined
- 2026-04-14 `[Human]` Deployed stack to Synology — `brian-mcp-memory` running on port 8765
- 2026-04-14 `[Code]` Confirmed MCP endpoint live: `http://192-168-0-64.aldarondo.direct.quickconnect.to:8765/mcp` returns 200
- 2026-04-14 `[Code]` Dockerfile created with CPU-only torch (image built locally, ~2GB)
- 2026-04-14 `[Human]` MCP server added to Claude Code — `brian-memory` connected
- 2026-04-14 `[Code]` Full round-trip validated: store → search (semantic + tag filter) → delete — **Phase 1 complete**

## 🚫 Blocked
<!-- log blockers here -->

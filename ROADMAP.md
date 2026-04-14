# brian-mcp Roadmap
> Tag key: `[Code]` = Claude Code · `[Cowork]` = Claude Cowork · `[Human]` = Charles must act

## 🎯 Current Milestone
Stack running on Synology, reachable on LAN, and at least one Claude Code session can store and retrieve a family-tagged memory.

## 🔄 In Progress
- [ ] `[Human]` Deploy stack to Synology and validate locally

## 🔲 Backlog

### Phase 1 — Local Deployment (LAN only)
- [ ] `[Human]` SSH into Synology, clone repo to `/volume1/docker/brian-mcp/`, copy `.env.example` → `.env` (no tunnel token needed yet), run `docker compose up -d`
- [ ] `[Human]` Confirm containers are running: `docker compose ps`
- [ ] `[Human]` Health check from home network: `curl http://192-168-0-64.aldarondo.direct.quickconnect.to:8765/health`
- [ ] `[Code]` Test `add_memory` / `search_memory` / `delete_memory` with family tags (`user:charles`, `user:*`)
- [ ] `[Human]` Add `http://192-168-0-64.aldarondo.direct.quickconnect.to:8765` as Remote MCP server in Claude Code settings
- [ ] `[Code]` Verify memory persists across Claude Code sessions

### Phase 2 — Public Exposure (Cloudflare Tunnel)
- [ ] `[Human]` Create Cloudflare Tunnel in dashboard for `brian.aldarondo.us/memory` → copy tunnel token
- [ ] `[Human]` Add `TUNNEL_TOKEN` to `.env` on Synology, restart stack: `docker compose up -d`
- [ ] `[Human]` Validate endpoint reachable externally: `curl https://brian.aldarondo.us/memory/health`
- [ ] `[Human]` Update Remote MCP server URL in Claude Code settings to `https://brian.aldarondo.us/memory`

### Phase 3 — Validate & Test
- [ ] `[Code]` Write integration tests for add/search/delete flows against live endpoint
- [ ] `[Code]` Write unit tests for any helper utilities

## ✅ Completed
- 2026-04-13 `[Code]` Initial scaffold — docker-compose.yml, .env.example, cloudflared config, tests/
- 2026-04-13 `[Code]` Game plan defined

## 🚫 Blocked
<!-- log blockers here -->

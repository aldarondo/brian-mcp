# brian-mcp Roadmap
> Tag key: `[Code]` = Claude Code · `[Cowork]` = Claude Cowork · `[Human]` = Charles must act

## 🎯 Current Milestone
Stable, always-on Remote MCP memory endpoint live at `https://brian.aldarondo.us/memory`.

## 🔄 In Progress
- [ ] `[Code]` Define project game plan

## 🔲 Backlog

### Phase 1 — Deploy
- [ ] `[Human]` Create Cloudflare Tunnel for `brian.aldarondo.us/memory` in Cloudflare dashboard → copy tunnel token
- [ ] `[Human]` SSH into Synology, clone repo to `/volume1/docker/brian-mcp/`, copy `.env.example` → `.env`, fill in `TUNNEL_TOKEN`, run `docker compose up -d`
- [ ] `[Human]` Validate endpoint is reachable externally: `curl https://brian.aldarondo.us/memory/health`
- [ ] `[Code]` Test `add_memory` / `search_memory` with family member tags (`user:charles`, `user:*`)
- [ ] `[Human]` Add `https://brian.aldarondo.us/memory` as a Remote MCP server in Claude Code settings

### Phase 2 — Validate
- [ ] `[Code]` Verify memory persists across Claude Code sessions
- [ ] `[Code]` Write integration tests for add/search/delete flows against live endpoint
- [ ] `[Code]` Write unit tests for any helper utilities

## ✅ Completed
- 2026-04-13 `[Code]` Initial scaffold — docker-compose.yml, .env.example, cloudflared config, tests/

## 🚫 Blocked
<!-- log blockers here -->

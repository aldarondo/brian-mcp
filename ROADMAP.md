# brian-mcp Roadmap
> Tag key: `[Code]` = Claude Code · `[Cowork]` = Claude Cowork · `[Human]` = Charles must act

## 🔄 In Progress
- [ ] `[Code]` Define project game plan

## 🔲 Backlog

### Phase 1 — Foundation
- [ ] `[Code]` Write `docker-compose.yml` for mcp-memory-service + cloudflared on Synology
- [ ] `[Code]` Write `.env.example` with all required environment variables
- [ ] `[Human]` Create Cloudflare Tunnel and get tunnel token
- [ ] `[Human]` Deploy stack to Synology NAS and verify containers start
- [ ] `[Code]` Set up persistent storage paths on Synology (`/volume1/docker/brian-mcp/memory/`)
- [ ] `[Human]` Validate endpoint is reachable from external network
- [ ] `[Code]` Test `add_memory`, `search_memory`, `delete_memory` via REST API
- [ ] `[Code]` Validate multi-user tagging (`user:charles`)

### Phase 2 — Claude Code Integration
- [ ] `[Human]` Add `brian.[domain].com/memory` as a Remote MCP server in Claude Code settings
- [ ] `[Code]` Verify memory persists across Claude Code sessions

### Testing
- [ ] `[Code]` Write unit tests for memory service helpers
- [ ] `[Code]` Write integration tests for end-to-end add/search/delete flows

## ✅ Completed
<!-- dated entries go here -->
- [ ] `[Code]` Initial scaffold — 2026-04-13

## 🚫 Blocked
<!-- log blockers here -->

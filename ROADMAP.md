# brian-mcp Roadmap
> Tag key: `[Code]` = Claude Code · `[Cowork]` = Claude Cowork · `[Human]` = Charles must act

## 🎯 Current Milestone
Project complete — maintenance mode. Rebuild ghcr.io image on mcp-memory-service updates; re-auth NAS if GitHub PAT expires.

## 🔄 In Progress
<!-- nothing active -->

## 🔲 Backlog
<!-- nothing pending -->

## ✅ Completed
- 2026-04-14 `[Code]` Initial scaffold — docker-compose.yml, .env.example, cloudflared config, tests/
- 2026-04-14 `[Code]` Game plan defined
- 2026-04-14 `[Human]` Deployed stack to Synology — `brian-mcp-memory` running on port 8765
- 2026-04-14 `[Code]` Confirmed MCP endpoint live on LAN (port 8765)
- 2026-04-14 `[Code]` Dockerfile created with CPU-only torch (~2GB)
- 2026-04-14 `[Human]` MCP server added to Claude Code — `brian-memory` connected
- 2026-04-14 `[Code]` Full round-trip validated: store → search (semantic + tag filter) → delete — **Phase 1 complete**
- 2026-04-19 `[Human]` Cloudflare Tunnel created, DNS `brian.aldarondo.family` CNAME set
- 2026-04-19 `[Code]` Ingress rule set via Cloudflare MCP — `brian.aldarondo.family` → `http://mcp-memory:8765`
- 2026-04-19 `[Code]` Tunnel live — `https://brian.aldarondo.family/mcp` returns 200 — **Phase 2 complete**
- 2026-04-19 `[Code]` MCP server URL updated in Claude Code to `https://brian.aldarondo.family/mcp`
- 2026-04-19 `[Code]` Cloudflare Access enabled — OTP policy for 4 family members, service token for Claude Code
- 2026-04-19 `[Code]` 8 integration tests passing against live authenticated endpoint — **Phase 3 complete**
- 2026-04-19 `[Human]` GitHub PAT with `write:packages` scope generated and stored in claude-synology/config.json
- 2026-04-19 `[Code]` Built CPU-only torch Docker image (~2GB, no CUDA), pushed to ghcr.io/aldarondo/brian-mcp-memory:latest
- 2026-04-19 `[Code]` Synology NAS authenticated to ghcr.io via /root/.docker/config.json, docker-compose.yml updated
- 2026-04-19 `[Code]` NAS container recreated from ghcr.io image — starts healthy in ~60s vs 3-5min before, 8/8 integration tests passing

## 🚫 Blocked
- ❌ [docker-monitor:deploy-failed] GitHub Actions deploy failed (run #24690343046) — https://github.com/aldarondo/brian-mcp/actions/runs/24690343046 — 2026-04-21 08:00 UTC
- ❌ [docker-monitor:no-weekly-schedule] No GitHub Actions workflows found — add a workflow with a `schedule:` trigger for weekly dependency rebuilds — 2026-04-20 17:07 UTC
<!-- log blockers here -->

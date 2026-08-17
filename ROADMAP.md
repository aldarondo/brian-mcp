# brian-mcp Roadmap
> Tag key: `[Code]` = Claude Code · `[Cowork]` = Claude Cowork · `[Human]` = Charles must act

## 🎯 Current Milestone
Project complete — maintenance mode. Rebuild ghcr.io image on mcp-memory-service updates; re-auth NAS if GitHub PAT expires.

## 🔄 In Progress
<!-- nothing active -->

## 🔲 Backlog

- `[Human]` Investigate GitHub Actions deploy failure (run #24748318702). Start here: check the Actions run log at https://github.com/aldarondo/brian-mcp/actions/runs/24748318702 — suspected cause is `cloudflared access ssh` command syntax or `nas-ssh.aldarondo.family` Cloudflare Access app config. If SSH via tunnel works locally (`cloudflared access ssh --hostname nas-ssh.aldarondo.family`), the issue is CI-specific.
- `[Human]` Replace SSH password auth in build.yml with SSH key auth: generate keypair, add public key to NAS `~/.ssh/authorized_keys`, add private key as `NAS_SSH_PRIVATE_KEY` GitHub Secret, replace `sshpass` with `webfactory/ssh-agent` action.
- `[Code]` Schedule the daily backup on the Synology (run from a local Claude Code session with SSH access to the NAS). Two options:
  1. **DSM Task Scheduler via API** (preferred — survives DSM upgrades): `ssh charles@synology` and use `synowebapi --exec api=SYNO.Core.TaskScheduler method=create version=1 ...` to register a daily 03:00 user-defined task that runs `/volume1/docker/brian-mcp/scripts/backup.sh` as root. Verify with `synowebapi --exec api=SYNO.Core.TaskScheduler method=list version=1`.
  2. **Root crontab fallback** (if the API path is brittle): append `0 3 * * * root /volume1/docker/brian-mcp/scripts/backup.sh` to `/etc/crontab`, then `synoservice --restart crond` (or `synoservicectl --reload crond`). Note: `/etc/crontab` may be reset on major DSM upgrades, so prefer option 1.
  Confirm the task is wired up by tailing `/volume1/docker/brian-mcp/backups/backup.log` after the first scheduled run, and check that `backups/memory-YYYY-MM-DD.tar.gz` appeared.
- `[Code]` Off-site backup via brian-drive — once the brian-drive project ships, wire it up as the off-site destination for `/volume1/docker/brian-mcp/backups/*.tar.gz`. Goal: weekly upload of the latest snapshot to Google Drive, with retention (e.g., 4 weekly + 6 monthly). Blocked on brian-drive being production-ready.
- `[Human]` Restore drill — quarterly test that the latest backup tarball actually rehydrates into a working container, using `scripts/restore.sh <tarball>` against a scratch directory. Run `tests/integration/` against it, confirm memory count and a known-good search match. Log each drill date here.

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
- 2026-04-22 `[Code]` QA audit — 40 findings fixed: scrubbed credentials from .env.test, fixed pytest filename collision, wrote real unit tests (test_helpers.py), added error-case integration tests, fixed search() return type + hash extraction + configurable timeout, fixed docker-compose TUNNEL_TOKEN validation + healthcheck logging, improved pre-commit hook warnings, added CI test job to build.yml, fixed StrictHostKeyChecking, removed outdated Dockerfile comment, updated .env.example with CF Access instructions, overhauled README with deployment checklist + troubleshooting, fixed CLAUDE.md health check URL, deleted unused cloudflared/config.yml
- 2026-04-22 `[Code]` Purged .env.test from git history using git filter-repo
- 2026-04-26 `[Code]` Local daily backup tooling — `scripts/backup.sh` (stop → tar → start with EXIT trap), `scripts/prune_backups.py` (7 daily + 4 weekly retention), `scripts/restore.sh` (archives existing memory dir before extract), 16 unit tests for prune logic. Synology Task Scheduler entry pending [Human] to schedule it overnight.

## 🚫 Blocked

<!-- log blockers here -->

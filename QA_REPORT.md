# QA Audit Report — brian-mcp
**Date:** 2026-04-22

## Executive Summary
Docker-based MCP memory server on Synology NAS, exposed via Cloudflare Tunnel. Production/maintenance mode, 16 files, 612 lines. Critical issues around secrets exposure, test infrastructure defects, and deployment automation failures.

**Total Findings: 40** — 6 Critical, 18 Major, 16 Minor

---

## 1. Bugs

### Critical

**1.1 Exposed Secrets in .env.test**
- **Location:** `.env.test` (lines 5-7)
- **Issue:** Live Cloudflare Access credentials committed to git:
  ```
  CF_ACCESS_CLIENT_ID=25bce525492e40c0ad803d71ecd5bba4.access
  CF_ACCESS_CLIENT_SECRET=79edeee9336dfd8e69c240a513e820657dead0289741f98db6a71f7ea09802e3
  ```
- **Rating:** Critical
- **Fix:** Revoke these tokens immediately in Cloudflare Zero Trust, regenerate with new values in a local-only `.env.test`, and use `git filter-repo` to purge from history.

**1.2 GitHub Actions Deploy Failure (Unresolved)**
- **Location:** `.github/workflows/build.yml` (lines 42-53), `ROADMAP.md` (line 34)
- **Issue:** Deployment marked BLOCKED in ROADMAP.md since 2026-04-22 08:00 UTC. Deployment cannot push container image updates to NAS.
- **Rating:** Critical

**1.3 Pytest Duplicate Filename Collision**
- **Location:** `tests/unit/test_placeholder.py` and `tests/integration/test_placeholder.py`
- **Issue:** Both files have the same name, causing pytest import mismatch. Running `pytest tests/` fails immediately.
- **Rating:** Critical
- **Fix:** Rename to unique names, e.g., `test_unit_placeholder.py` and `test_integration_placeholder.py`.

### Major

**1.4 Pre-commit Hook Fails Silently on Missing Dependencies**
- **Location:** `.githooks/pre-commit` (lines 20-27)
- **Issue:** Hook silently exits with code 0 if `.hub/` directory or `node` is missing, allowing commits of secrets.
- **Rating:** Major

**1.5 Environment Variables Undefined in Production**
- **Location:** `docker-compose.yml` (lines 7-12)
- **Issue:** `TUNNEL_TOKEN: ${TUNNEL_TOKEN:-}` defaults to empty string, not error. Silent misconfiguration risk.
- **Rating:** Major

### Minor

**1.6 Hardcoded Timeout in Test Helper**
- **Location:** `tests/integration/test_mcp_endpoint.py` (line 21)
- **Issue:** `TIMEOUT = 30` is hardcoded. Make configurable via `MCP_TEST_TIMEOUT` env var.
- **Rating:** Minor

---

## 2. Test Coverage

### Critical

**2.1 Unit Tests Are Placeholder Stubs**
- **Location:** `tests/unit/test_placeholder.py` (lines 5-14)
- **Issue:** All unit tests are skipped with `@pytest.mark.skip`. Zero unit test coverage. Violates CLAUDE.md testing requirements.
- **Rating:** Critical

**2.2 Integration Tests Partially Implemented**
- **Location:** `tests/integration/test_placeholder.py` (lines 11-24)
- **Issue:** Two core workflows (`add_and_search_memory`, `delete_memory`) are placeholder stubs.
- **Rating:** Critical

**2.3 Integration Test Suite Incomplete**
- **Location:** `tests/integration/test_mcp_endpoint.py`
- **Missing:** Error handling, auth failure scenarios, rate limiting, edge cases, concurrent operations.
- **Rating:** Critical

---

## 3. Code Quality

### Major

**3.1 Fragile Hash Extraction in Test Helper**
- **Location:** `tests/integration/test_mcp_endpoint.py` (lines 66-79)
- **Issue:** Loose regex matches any 32+ char hex string. Tests could pass on malformed responses.
- **Rating:** Major

**3.2 Fragile Search Result Parsing**
- **Location:** `tests/integration/test_mcp_endpoint.py` (lines 82-89)
- **Issue:** Returns raw text; callers must do string matching. Brittle and format-dependent.
- **Rating:** Major

**3.3 Hardcoded Magic Strings**
- **Location:** `tests/integration/test_mcp_endpoint.py` (lines 23-24)
- **Rating:** Major

**3.4 No Logging in Docker Healthcheck**
- **Location:** `docker-compose.yml` (lines 23-29)
- **Issue:** Inline healthcheck Python produces no error output on failure. Hard to debug.
- **Rating:** Major

### Minor

**3.5–3.7:** No tests README, inconsistent error handling, no type hints.

---

## 4. Documentation

### Major

**4.1 Deployment Instructions Incomplete**
- **Location:** `README.md` (lines 31-48)
- **Issue:** Missing instructions for obtaining `CF_ACCESS_CLIENT_ID/SECRET` and `docker login ghcr.io`.
- **Rating:** Major

**4.2 CLAUDE.md Testing Requirements Violated**
- Zero unit tests, incomplete integration tests violate stated policy.
- **Rating:** Major

**4.3 Health Check Instructions Outdated**
- **Location:** `CLAUDE.md` (line 39), `README.md` (line 68)
- **Issue:** Inconsistent URLs — one uses `/health`, one uses no path. Actual endpoint is `/mcp`.
- **Rating:** Major

**4.4 No Deployment Checklist**
- **Rating:** Major

### Minor

**4.5–4.7:** Outdated Dockerfile comment, no architecture diagram, no troubleshooting guide.

---

## 5. Organization

### Major

**5.1 Git History Polluted with Docker-Monitor Commits**
- Multiple `chore: docker-monitor deploy-failed` commits obscure real history.
- **Rating:** Major

**5.2 Blocking Issue Not Resolved**
- Deploy failure at ROADMAP.md line 34 has no investigation notes or assigned owner.
- **Rating:** Major

**5.3 No CI/CD Test Automation**
- **Location:** `.github/workflows/`
- Neither workflow runs tests before deploying to NAS.
- **Rating:** Major

**5.4 No Issue/PR Templates**
- **Rating:** Major

### Minor

**5.5–5.7:** Unused cloudflared config, no local dev setup, no CONTRIBUTING.md.

---

## 6. Security

### Critical

**6.1 Live Credentials in Committed .env.test**
- See Bug 1.1. Revoke and purge from history immediately.
- **Rating:** Critical

### Major

**6.2 SSH Password in CI/CD (Not Key-Based)**
- **Location:** `.github/workflows/build.yml` (lines 43-47)
- **Issue:** `sshpass` with plaintext password. Use SSH key-based auth instead.
- **Rating:** Major

**6.3 Service Token in Plaintext .env on NAS**
- If NAS is compromised, Cloudflare service token is exposed.
- **Rating:** Major

**6.4 No Rate Limiting on MCP Endpoint**
- Authenticated users can DoS the service.
- **Rating:** Major

### Minor

**6.5–6.10:** StrictHostKeyChecking disabled, no secret scanning, HTTP health check, no CORS docs, no audit logging, overly permissive restart policy.

---

## Summary

| Category | Critical | Major | Minor |
|----------|----------|-------|-------|
| Bugs | 3 | 2 | 1 |
| Test Coverage | 3 | 0 | 0 |
| Code Quality | 0 | 4 | 3 |
| Documentation | 0 | 4 | 3 |
| Organization | 0 | 4 | 3 |
| Security | 1 | 3 | 5 |
| **Total** | **7** | **17** | **15** |

---

## Top Priority Actions

1. **Revoke Cloudflare Access tokens** in `.env.test` immediately — live credentials in git history
2. **Fix pytest collision** — rename duplicate `test_placeholder.py` files so tests can run at all
3. **Investigate deploy failure** — GitHub Actions has been failing since 2026-04-22 08:00 UTC

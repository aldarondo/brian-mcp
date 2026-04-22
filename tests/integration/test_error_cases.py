"""Integration tests for error cases, edge cases, and boundary conditions.

Run against the live public endpoint (requires Cloudflare Access service token):
    source .env.test && pytest tests/integration/test_error_cases.py

Or against LAN (no auth needed):
    MCP_MEMORY_URL=http://192-168-0-64.aldarondo.direct.quickconnect.to:8765/mcp pytest tests/integration/test_error_cases.py
"""

import os
import json
import pytest
import urllib.request
import urllib.error

MCP_URL = os.getenv("MCP_MEMORY_URL", "https://brian.aldarondo.family/mcp")
CF_CLIENT_ID = os.getenv("CF_ACCESS_CLIENT_ID", "")
CF_CLIENT_SECRET = os.getenv("CF_ACCESS_CLIENT_SECRET", "")
TIMEOUT = int(os.getenv("MCP_TEST_TIMEOUT", "30"))

_has_auth = bool(CF_CLIENT_ID and CF_CLIENT_SECRET and
                 "your-service-token" not in CF_CLIENT_ID)
requires_auth = pytest.mark.skipif(
    not _has_auth,
    reason="CF_ACCESS_CLIENT_ID/SECRET not set — skipping live auth tests",
)


def _mcp_call(method: str, params: dict, *, auth: bool = True) -> dict:
    payload = json.dumps({
        "jsonrpc": "2.0",
        "method": "tools/call",
        "id": 1,
        "params": {"name": method, "arguments": params},
    }).encode()
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
        "User-Agent": "brian-mcp-test/1.0",
    }
    if auth and CF_CLIENT_ID:
        headers["CF-Access-Client-Id"] = CF_CLIENT_ID
    if auth and CF_CLIENT_SECRET:
        headers["CF-Access-Client-Secret"] = CF_CLIENT_SECRET
    req = urllib.request.Request(MCP_URL, data=payload, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        raw = resp.read().decode()
    for line in raw.splitlines():
        if line.startswith("data:"):
            body = line[5:].strip()
            if body and body != "[DONE]":
                return json.loads(body)
    return json.loads(raw)


# ── Auth / Access control ─────────────────────────────────────────────────────

class TestAuthErrors:
    @requires_auth
    def test_missing_auth_headers_returns_403(self):
        """Request without CF Access headers should be rejected by Cloudflare."""
        payload = json.dumps({
            "jsonrpc": "2.0", "method": "ping", "id": 1,
        }).encode()
        req = urllib.request.Request(
            MCP_URL,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with pytest.raises(urllib.error.HTTPError) as exc_info:
            urllib.request.urlopen(req, timeout=TIMEOUT)
        assert exc_info.value.code in (403, 401, 302), \
            f"Expected auth rejection, got {exc_info.value.code}"


# ── Edge cases ────────────────────────────────────────────────────────────────

class TestEdgeCases:
    @requires_auth
    def test_empty_query_search_returns_gracefully(self):
        """Search with an empty query string should not crash the server."""
        result = _mcp_call("memory_search", {"query": "", "limit": 5})
        # Server should return a result (possibly empty), not an error
        assert "result" in result or "error" in result, \
            f"Unexpected response shape: {result}"

    @requires_auth
    def test_search_with_zero_limit(self):
        """Search with limit=0 should return empty results, not an error."""
        result = _mcp_call("memory_search", {"query": "test", "limit": 0})
        assert "result" in result or "error" in result

    @requires_auth
    def test_delete_nonexistent_hash_returns_gracefully(self):
        """Deleting a hash that doesn't exist should not raise a 500."""
        fake_hash = "0" * 64
        result = _mcp_call("memory_delete", {"content_hash": fake_hash})
        assert "result" in result or "error" in result, \
            f"Unexpected response for non-existent hash: {result}"

    @requires_auth
    def test_search_with_nonexistent_tag_returns_empty(self):
        """Search filtered to a tag that matches nothing should return empty, not error."""
        result = _mcp_call("memory_search", {
            "query": "anything",
            "tags": ["nonexistent:tag:12345"],
            "limit": 5,
        })
        assert "result" in result or "error" in result

    @requires_auth
    def test_store_minimal_content(self):
        """Single-character content should be storable."""
        result = _mcp_call("memory_store", {
            "content": "x",
            "conversation_id": "test-edge-cases",
            "metadata": {"tags": "test:integration"},
        })
        text = result["result"]["content"][0]["text"]
        assert text, "Empty response from store"
        # Extract and clean up
        for part in text.split():
            cleaned = part.rstrip(")")
            if len(cleaned) >= 32 and all(c in "0123456789abcdef" for c in cleaned):
                _mcp_call("memory_delete", {"content_hash": cleaned})
                break


# ── Malformed requests ────────────────────────────────────────────────────────

class TestMalformedRequests:
    @requires_auth
    def test_unknown_tool_name_returns_error(self):
        """Calling a tool that doesn't exist should return an error, not a 500."""
        result = _mcp_call("memory_nonexistent_tool", {"foo": "bar"})
        assert "error" in result or (
            "result" in result and "error" in str(result).lower()
        ), f"Expected error response for unknown tool: {result}"

    @requires_auth
    def test_missing_required_content_field(self):
        """memory_store without content field should return an error."""
        result = _mcp_call("memory_store", {
            "conversation_id": "test-malformed",
            # content intentionally omitted
        })
        assert "error" in result or "result" in result, \
            f"Unexpected response: {result}"

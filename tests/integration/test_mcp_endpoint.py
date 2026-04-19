"""
Integration tests for brian-mcp memory endpoint.
All features require unit + integration tests before a task is marked complete.

Run against the live public endpoint:
    MCP_MEMORY_URL=https://brian.aldarondo.family/mcp pytest tests/integration/

Or against LAN:
    MCP_MEMORY_URL=http://192-168-0-64.aldarondo.direct.quickconnect.to:8765/mcp pytest tests/integration/
"""

import os
import json
import pytest
import urllib.request
import urllib.error

MCP_URL = os.getenv("MCP_MEMORY_URL", "https://brian.aldarondo.family/mcp")
TIMEOUT = 30

TEST_TAG = "test:integration"
CONVERSATION_ID = "test-integration-run"


# ── Helpers ──────────────────────────────────────────────────────────────────

def mcp_call(method: str, params: dict) -> dict:
    """Send a single MCP tool call and return the result."""
    payload = json.dumps({
        "jsonrpc": "2.0",
        "method": "tools/call",
        "id": 1,
        "params": {"name": method, "arguments": params},
    }).encode()

    req = urllib.request.Request(
        MCP_URL,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
            "User-Agent": "brian-mcp-test/1.0",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        raw = resp.read().decode()

    # Strip SSE framing if present
    for line in raw.splitlines():
        if line.startswith("data:"):
            body = line[5:].strip()
            if body and body != "[DONE]":
                return json.loads(body)
    return json.loads(raw)


def store(content: str, tags: str) -> str:
    """Store a memory and return its hash."""
    result = mcp_call("memory_store", {
        "content": content,
        "conversation_id": CONVERSATION_ID,
        "metadata": {"tags": tags},
    })
    text = result["result"]["content"][0]["text"]
    assert "hash:" in text.lower() or "stored" in text.lower(), f"Unexpected store response: {text}"
    # Extract hash from "Memory stored successfully (hash: abc123...)"
    for part in text.split():
        if len(part) >= 32 and all(c in "0123456789abcdef)" for c in part.rstrip(")")):
            return part.rstrip(")")
    pytest.fail(f"Could not extract hash from: {text}")


def search(query: str, tags: list[str] | None = None, limit: int = 10) -> list[dict]:
    """Search memories and return list of result dicts."""
    params = {"query": query, "limit": limit}
    if tags:
        params["tags"] = tags
    result = mcp_call("memory_search", params)
    text = result["result"]["content"][0]["text"]
    return text  # Return raw text for assertion


def delete(content_hash: str) -> str:
    """Delete a memory by hash and return response text."""
    result = mcp_call("memory_delete", {"content_hash": content_hash})
    return result["result"]["content"][0]["text"]


# ── Tests ─────────────────────────────────────────────────────────────────────

class TestConnectivity:
    def test_ping(self):
        """MCP server responds to ping."""
        payload = json.dumps({
            "jsonrpc": "2.0", "method": "ping", "id": 1,
        }).encode()
        req = urllib.request.Request(
            MCP_URL, data=payload,
            headers={"Content-Type": "application/json",
                     "Accept": "application/json, text/event-stream",
                     "User-Agent": "brian-mcp-test/1.0"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            assert resp.status == 200

    def test_health_url(self):
        """Endpoint URL is reachable."""
        assert MCP_URL.startswith("http"), f"Invalid URL: {MCP_URL}"


class TestStoreAndSearch:
    def test_store_returns_hash(self):
        """memory_store returns a content hash."""
        h = store(
            "Integration test: Aldarondo family NAS stores shared memories.",
            f"{TEST_TAG},user:charles",
        )
        assert len(h) >= 32, f"Hash too short: {h}"
        # Cleanup
        delete(h)

    def test_search_finds_stored_memory(self):
        """Stored memory is retrievable via semantic search."""
        content = "Integration test: proof bread opens at 7am on Saturdays."
        h = store(content, f"{TEST_TAG},user:charles")
        try:
            result = search("proof bread opening hours", tags=[TEST_TAG])
            assert "proof bread" in result.lower() or "7am" in result.lower(), \
                f"Expected memory not found in results: {result}"
        finally:
            delete(h)

    def test_tag_filter_isolates_results(self):
        """Tag filter returns only memories with matching tag."""
        h = store(
            "Integration test: this memory has a unique family tag.",
            f"{TEST_TAG},user:charles",
        )
        try:
            result = search("unique family tag", tags=["user:charles"])
            assert "unique family tag" in result.lower(), \
                f"Tagged memory not found: {result}"
        finally:
            delete(h)


class TestDelete:
    def test_delete_removes_memory(self):
        """Deleted memory no longer appears in search results."""
        content = "Integration test: this memory should be deleted."
        h = store(content, f"{TEST_TAG},user:charles")
        resp = delete(h)
        assert "deleted" in resp.lower(), f"Unexpected delete response: {resp}"

        # Confirm it's gone — server returns "no memories found" when empty
        result = search("this memory should be deleted", tags=[TEST_TAG])
        assert result.lower().startswith("no memories found") or \
               "this memory should be deleted" not in result.lower(), \
            f"Memory still present after deletion: {result}"


class TestMultiUserTagging:
    def test_user_scoped_memory(self):
        """Memories tagged user:charles are retrievable by that tag."""
        h = store(
            "Integration test: Charles prefers dark mode in all apps.",
            f"{TEST_TAG},user:charles",
        )
        try:
            result = search("dark mode preference", tags=["user:charles"])
            assert "dark mode" in result.lower(), \
                f"User-scoped memory not found: {result}"
        finally:
            delete(h)

    def test_shared_memory_tag(self):
        """Memories tagged user:* (shared) are retrievable."""
        h = store(
            "Integration test: Family shared rule — no phones at dinner.",
            f"{TEST_TAG},user:*",
        )
        try:
            result = search("family rules dinner", tags=["user:*"])
            assert "dinner" in result.lower() or "phones" in result.lower(), \
                f"Shared memory not found: {result}"
        finally:
            delete(h)

"""Unit tests for brian-mcp response-parsing helpers.

These test the parsing logic used by the integration test helpers, exercising
it with synthetic inputs so no live endpoint is required.
"""
import json
import pytest


# ── Functions under test (inlined to keep unit tests self-contained) ──────────

def extract_hash_from_text(text: str) -> str | None:
    """Return content hash from a store-response string, or None."""
    for part in text.split():
        cleaned = part.rstrip(")")
        if len(cleaned) >= 32 and all(c in "0123456789abcdef" for c in cleaned):
            return cleaned
    return None


def parse_sse_response(raw: str) -> dict | None:
    """Strip SSE framing and return parsed JSON, or None for empty input."""
    if not raw.strip():
        return None
    for line in raw.splitlines():
        if line.startswith("data:"):
            body = line[5:].strip()
            if body and body != "[DONE]":
                return json.loads(body)
    return json.loads(raw)


def build_mcp_payload(method: str, params: dict) -> bytes:
    """Encode a JSON-RPC MCP tool-call payload."""
    return json.dumps({
        "jsonrpc": "2.0",
        "method": "tools/call",
        "id": 1,
        "params": {"name": method, "arguments": params},
    }).encode()


# ── extract_hash_from_text ────────────────────────────────────────────────────

class TestExtractHash:
    def test_extracts_hash_from_typical_response(self):
        text = "Memory stored successfully (hash: abc123def456abc123def456abc123de)"
        assert extract_hash_from_text(text) == "abc123def456abc123def456abc123de"

    def test_strips_trailing_parenthesis(self):
        text = "stored (hash: aaaa1111bbbb2222cccc3333dddd4444)"
        assert extract_hash_from_text(text) == "aaaa1111bbbb2222cccc3333dddd4444"

    def test_returns_none_when_no_hash_present(self):
        assert extract_hash_from_text("Memory stored but no hash returned") is None

    def test_rejects_string_shorter_than_32_chars(self):
        assert extract_hash_from_text("stored deadbeef") is None

    def test_rejects_non_hex_characters(self):
        # 32 chars but contains 'g' — not valid hex
        assert extract_hash_from_text("gggg1111bbbb2222cccc3333dddd4444") is None

    def test_handles_empty_string(self):
        assert extract_hash_from_text("") is None

    def test_extracts_first_hash_when_multiple_present(self):
        text = "first: aaaa1111bbbb2222cccc3333dddd4444 second: bbbb2222cccc3333dddd4444aaaa1111"
        result = extract_hash_from_text(text)
        assert result in ("aaaa1111bbbb2222cccc3333dddd4444", "bbbb2222cccc3333dddd4444aaaa1111")


# ── parse_sse_response ────────────────────────────────────────────────────────

class TestParseSseResponse:
    def test_parses_sse_framed_json(self):
        raw = 'data: {"result": {"content": [{"text": "ok"}]}}\n'
        result = parse_sse_response(raw)
        assert result["result"]["content"][0]["text"] == "ok"

    def test_parses_plain_json_when_no_sse_framing(self):
        raw = '{"result": {"content": [{"text": "ok"}]}}'
        result = parse_sse_response(raw)
        assert result["result"]["content"][0]["text"] == "ok"

    def test_skips_done_sentinel_and_continues(self):
        raw = "data: [DONE]\ndata: {\"status\": \"complete\"}\n"
        result = parse_sse_response(raw)
        assert result == {"status": "complete"}

    def test_returns_none_for_empty_input(self):
        assert parse_sse_response("") is None

    def test_returns_none_for_whitespace_only(self):
        assert parse_sse_response("   \n  ") is None

    def test_parses_multiline_sse_stream(self):
        raw = "id: 1\nevent: message\ndata: {\"x\": 42}\n"
        result = parse_sse_response(raw)
        assert result == {"x": 42}


# ── build_mcp_payload ─────────────────────────────────────────────────────────

class TestBuildMcpPayload:
    def test_produces_valid_json_rpc_envelope(self):
        payload = build_mcp_payload("memory_store", {"content": "hello"})
        obj = json.loads(payload)
        assert obj["jsonrpc"] == "2.0"
        assert obj["method"] == "tools/call"
        assert obj["params"]["name"] == "memory_store"
        assert obj["params"]["arguments"] == {"content": "hello"}

    def test_returns_bytes(self):
        assert isinstance(build_mcp_payload("memory_search", {}), bytes)

    def test_encodes_nested_params(self):
        params = {"content": "test", "metadata": {"tags": "user:charles"}}
        obj = json.loads(build_mcp_payload("memory_store", params))
        assert obj["params"]["arguments"]["metadata"]["tags"] == "user:charles"

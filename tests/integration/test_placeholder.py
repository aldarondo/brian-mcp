# All features require unit + integration tests before a task is marked complete.
# Integration tests hit the live mcp-memory-service HTTP endpoint.
# Set MCP_MEMORY_URL in your environment before running (e.g. http://localhost:8765).
import pytest
import os


MCP_URL = os.getenv("MCP_MEMORY_URL", "http://localhost:8765")


@pytest.mark.skip(reason="placeholder — replace with real integration tests")
def test_add_and_search_memory():
    """Integration stub: add a memory then retrieve it via search."""
    # import httpx
    # r = httpx.post(f"{MCP_URL}/add", json={"content": "test", "tags": ["user:charles"]})
    # assert r.status_code == 200
    pass


@pytest.mark.skip(reason="placeholder — replace with real integration tests")
def test_delete_memory():
    """Integration stub: add then delete a memory and confirm it's gone."""
    pass

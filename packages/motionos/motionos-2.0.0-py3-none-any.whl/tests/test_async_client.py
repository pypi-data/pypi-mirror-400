"""
Unit tests for MotionOS async client.
"""

import pytest
import respx
from httpx import Response
from motionos import AsyncMotionOS, IngestResult, RetrievalResult


@pytest.mark.asyncio
class TestAsyncMotionOS:
    """Test async client."""

    @pytest.fixture
    def client(self):
        """Create a test async client."""
        return AsyncMotionOS(api_key="sb_secret_test123", project_id="proj-123", debug=False)

    @pytest.mark.asyncio
    async def test_async_ingest(self, client):
        """Test async ingest."""
        with respx.mock:
            respx.post("https://api.motionos.ai/v1/memory/ingest").mock(
                return_value=Response(
                    200,
                    json={"id": "mem-123", "summary": "Summary", "version_id": "ver-456"},
                )
            )

            result = await client.ingest("Test memory")
            assert isinstance(result, IngestResult)
            assert result.id == "mem-123"

        await client.close()

    @pytest.mark.asyncio
    async def test_async_retrieve(self, client):
        """Test async retrieve."""
        with respx.mock:
            respx.post("https://api.motionos.ai/v1/memory/retrieve").mock(
                return_value=Response(
                    200,
                    json={
                        "context": "Test context",
                        "items": [],
                        "meta": {"mode": "retrieval", "format": "inject", "limit": 5},
                        "reasoning": "semantic",
                    },
                )
            )

            result = await client.retrieve("test query")
            assert isinstance(result, RetrievalResult)
            assert result.context == "Test context"

        await client.close()

    @pytest.mark.asyncio
    async def test_context_manager(self):
        """Test async context manager."""
        async with AsyncMotionOS(api_key="sb_secret_test123", project_id="proj-123") as client:
            assert client is not None


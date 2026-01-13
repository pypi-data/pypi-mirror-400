"""
Unit tests for MotionOS sync client.
"""

import pytest
import responses
from motionos import MotionOS, IngestResult, RetrievalResult, RollbackResult
from motionos.errors import (
    MotionOSError,
    InvalidAPIKeyError,
    InvalidRequestError,
    ForbiddenError,
    RateLimitError,
)


@pytest.fixture
def client():
    """Create a test client."""
    return MotionOS(api_key="sb_secret_test123", project_id="proj-123", debug=False)


class TestMotionOSInitialization:
    """Test client initialization."""

    def test_init_with_valid_options(self):
        """Test initialization with valid options."""
        client = MotionOS(api_key="sb_secret_test123", project_id="proj-123")
        assert client.project_id == "proj-123"
        assert client.base_url == "https://api.motionos.ai"

    def test_init_with_invalid_api_key(self):
        """Test initialization with invalid API key."""
        with pytest.raises(InvalidAPIKeyError):
            MotionOS(api_key="invalid_key", project_id="proj-123")

    def test_init_with_empty_project_id(self):
        """Test initialization with empty project ID."""
        with pytest.raises(InvalidRequestError):
            MotionOS(api_key="sb_secret_test123", project_id="")

    def test_init_with_custom_base_url(self):
        """Test initialization with custom base URL."""
        client = MotionOS(
            api_key="sb_secret_test123", project_id="proj-123", base_url="https://custom.api.com"
        )
        assert client.base_url == "https://custom.api.com"


class TestIngest:
    """Test ingest method."""

    @responses.activate
    def test_ingest_with_string(self, client):
        """Test ingest with string input."""
        responses.add(
            responses.POST,
            "https://api.motionos.ai/v1/memory/ingest",
            json={"id": "mem-123", "summary": "Test summary", "version_id": "ver-456"},
            status=200,
        )

        result = client.ingest("Test memory")
        assert isinstance(result, IngestResult)
        assert result.id == "mem-123"
        assert result.summary == "Test summary"
        assert result.version_id == "ver-456"

    @responses.activate
    def test_ingest_with_options(self, client):
        """Test ingest with options dict."""
        responses.add(
            responses.POST,
            "https://api.motionos.ai/v1/memory/ingest",
            json={"id": "mem-123", "summary": "Summary", "version_id": "ver-456"},
            status=200,
        )

        result = client.ingest(
            {
                "raw_text": "Test memory",
                "agent_id": "agent-1",
                "tags": ["tag1"],
            }
        )
        assert result.id == "mem-123"

    def test_ingest_with_empty_string(self, client):
        """Test ingest with empty string."""
        with pytest.raises(InvalidRequestError):
            client.ingest("")

    def test_ingest_with_invalid_importance(self, client):
        """Test ingest with invalid importance score."""
        with pytest.raises(InvalidRequestError):
            client.ingest({"raw_text": "test", "importance": 2.0})


class TestRetrieve:
    """Test retrieve method."""

    @responses.activate
    def test_retrieve_with_string(self, client):
        """Test retrieve with string query."""
        responses.add(
            responses.POST,
            "https://api.motionos.ai/v1/memory/retrieve",
            json={
                "context": "Test context",
                "items": [],
                "meta": {"mode": "retrieval", "format": "inject", "limit": 5},
                "reasoning": "semantic",
            },
            status=200,
        )

        result = client.retrieve("test query")
        assert isinstance(result, RetrievalResult)
        assert result.context == "Test context"
        assert result.meta["format"] == "inject"

    @responses.activate
    def test_retrieve_with_options(self, client):
        """Test retrieve with options dict."""
        responses.add(
            responses.POST,
            "https://api.motionos.ai/v1/memory/retrieve",
            json={
                "context": "",
                "items": [
                    {
                        "id": "mem-1",
                        "content": "Content",
                        "summary": "Summary",
                        "metadata": {},
                        "created_at": "2024-01-01T00:00:00Z",
                        "updated_at": "2024-01-01T00:00:00Z",
                        "score": 0.9,
                    }
                ],
                "meta": {"mode": "retrieval", "format": "raw", "limit": 10},
                "reasoning": "semantic",
            },
            status=200,
        )

        result = client.retrieve({"query": "test", "mode": "raw", "limit": 10})
        assert len(result.items) == 1
        assert result.items[0].id == "mem-1"

    def test_retrieve_with_invalid_limit(self, client):
        """Test retrieve with invalid limit."""
        with pytest.raises(InvalidRequestError):
            client.retrieve({"limit": 0})
        with pytest.raises(InvalidRequestError):
            client.retrieve({"limit": 51})


class TestRollback:
    """Test rollback method."""

    @responses.activate
    def test_rollback_success(self, client):
        """Test successful rollback."""
        from motionos.types import RollbackOptions

        responses.add(
            responses.POST,
            "https://api.motionos.ai/v1/memory/mem-123/rollback",
            json={"ok": True},
            status=200,
        )

        result = client.rollback(RollbackOptions(memory_id="mem-123", version_id="ver-456"))
        assert isinstance(result, RollbackResult)
        assert result.ok is True

    def test_rollback_with_invalid_params(self, client):
        """Test rollback with invalid parameters."""
        from motionos.types import RollbackOptions

        with pytest.raises(InvalidRequestError):
            client.rollback(RollbackOptions(memory_id="", version_id="ver-456"))


class TestBatchIngest:
    """Test batch ingest method."""

    @responses.activate
    def test_batch_ingest(self, client):
        """Test batch ingest."""
        from motionos.types import BatchIngestOptions

        responses.add(
            responses.POST,
            "https://api.motionos.ai/v1/memory/ingest",
            json={"id": "mem-123", "summary": "Summary", "version_id": "ver-456"},
            status=200,
        )

        result = client.batch_ingest(
            BatchIngestOptions(items=[{"raw_text": "Item 1"}, {"raw_text": "Item 2"}])
        )
        assert len(result.results) == 2


class TestUtilityMethods:
    """Test utility methods."""

    def test_get_config(self, client):
        """Test get_config method."""
        config = client.get_config()
        assert config.project_id == "proj-123"
        assert config.base_url == "https://api.motionos.ai"
        assert config.debug is False

    def test_set_default_agent(self, client):
        """Test set_default_agent method."""
        result = client.set_default_agent("agent-1")
        assert result is client  # Should return self for chaining
        assert client.default_agent == "agent-1"


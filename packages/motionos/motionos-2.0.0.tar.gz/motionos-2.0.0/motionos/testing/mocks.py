"""
MotionOS SDK - Test Mocks

Mock implementations for testing.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime


def mock_ingest_result(overrides: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Create a mock ingest result."""
    result = {
        "id": "mock_memory_id_123",
        "summary": "Mock memory ingested successfully",
        "version_id": "mock_version_id_456",
        "deduplicated": False,
        "metadata": {"mock": True},
    }
    if overrides:
        result.update(overrides)
    return result


def mock_retrieval_result(overrides: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Create a mock retrieval result."""
    result = {
        "context": "Mock context for testing",
        "items": [
            {
                "id": "mock_item_1",
                "summary": "Mock memory item",
                "content": "This is mock content for testing",
                "metadata": {"mock": True},
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "score": 0.95,
            }
        ],
        "reasoning": "mock",
        "meta": {
            "mode": "retrieval",
            "format": "inject",
            "limit": 5,
        },
        "confidence": 1.0,
    }
    if overrides:
        result.update(overrides)
    return result


def mock_timeline_walk_result(overrides: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Create a mock timeline walk result."""
    result = {
        "start_version_id": "mock_start_version",
        "nodes": [],
        "edges": [],
        "depth": 0,
        "total_visited": 0,
        "truncated": False,
    }
    if overrides:
        result.update(overrides)
    return result


def mock_validity_result(overrides: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Create a mock validity result."""
    result = {
        "version_id": "mock_version_id",
        "is_valid": True,
        "reason": "Mock validity check passed",
        "superseded_by": [],
        "latest_in_chain": "mock_version_id",
        "confidence_score": 1.0,
        "age_hours": 0,
    }
    if overrides:
        result.update(overrides)
    return result


class MockHTTPClient:
    """Mock HTTP client for testing."""
    
    def __init__(self, responses: Optional[Dict[str, Any]] = None):
        self.responses = responses or {}
        self.call_history: List[Dict[str, Any]] = []
    
    def add_response(self, pattern: str, response: Any, status: int = 200) -> None:
        """Add a mock response for a URL pattern."""
        self.responses[pattern] = {"data": response, "status": status}
    
    async def request(
        self,
        method: str,
        url: str,
        **kwargs,
    ) -> Dict[str, Any]:
        """Mock request method."""
        self.call_history.append({
            "method": method,
            "url": url,
            "kwargs": kwargs,
        })
        
        for pattern, response_info in self.responses.items():
            if pattern in url:
                return response_info["data"]
        
        raise Exception(f"No mock response for {url}")
    
    def get_calls(self) -> List[Dict[str, Any]]:
        """Get call history."""
        return self.call_history
    
    def reset(self) -> None:
        """Reset call history."""
        self.call_history = []

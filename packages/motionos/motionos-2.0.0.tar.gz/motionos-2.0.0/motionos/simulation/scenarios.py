"""
MotionOS SDK - Simulation Scenarios

Predefined scenarios for testing different conditions.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any
from uuid import uuid4
import base64
import time


@dataclass
class SimulationConfig:
    """Simulation mode configuration."""
    enabled: bool = True
    latency_ms: int = 50
    error_rate: float = 0.0
    rate_limit_after: Optional[int] = None
    responses: Optional[Dict[str, Any]] = None


class Scenarios:
    """Pre-built simulation scenarios."""
    
    @staticmethod
    def happy_path() -> SimulationConfig:
        """Happy path - all requests succeed with minimal latency."""
        return SimulationConfig(enabled=True, latency_ms=50, error_rate=0)
    
    @staticmethod
    def slow_network() -> SimulationConfig:
        """High latency environment (simulates slow network)."""
        return SimulationConfig(enabled=True, latency_ms=2000, error_rate=0)
    
    @staticmethod
    def rate_limited(after_requests: int = 5) -> SimulationConfig:
        """Rate limited after N requests."""
        return SimulationConfig(
            enabled=True, 
            latency_ms=50, 
            rate_limit_after=after_requests,
            error_rate=0,
        )
    
    @staticmethod
    def unstable(error_rate: float = 0.10) -> SimulationConfig:
        """Intermittent failures (10% error rate by default)."""
        return SimulationConfig(enabled=True, latency_ms=100, error_rate=error_rate)
    
    @staticmethod
    def offline() -> SimulationConfig:
        """Complete outage (100% failures)."""
        return SimulationConfig(enabled=True, latency_ms=100, error_rate=1.0)
    
    @staticmethod
    def timeout() -> SimulationConfig:
        """Timeout scenario (very high latency)."""
        return SimulationConfig(enabled=True, latency_ms=15000, error_rate=0)
    
    @staticmethod
    def custom(**kwargs) -> SimulationConfig:
        """Custom scenario builder."""
        return SimulationConfig(enabled=True, **kwargs)


def generate_simulation_id(operation: str, seed: Optional[str] = None) -> str:
    """Generate a deterministic response ID based on operation."""
    base = seed or operation
    encoded = base64.b64encode(base.encode()).decode()[:8]
    timestamp = hex(int(time.time() * 1000))[2:][:8]
    return f"sim_{encoded}_{timestamp}"


class MockData:
    """Simulation mode data generators."""
    
    @staticmethod
    def ingest_result(seed: Optional[str] = None) -> dict:
        """Generate a mock ingest result."""
        return {
            "id": generate_simulation_id("ingest", seed),
            "summary": "Simulated memory stored successfully",
            "version_id": generate_simulation_id("version", seed),
            "deduplicated": False,
            "metadata": {"simulation": True},
        }
    
    @staticmethod
    def retrieval_result(query: Optional[str] = None) -> dict:
        """Generate a mock retrieval result."""
        return {
            "context": f"[Simulation Mode] Context for query: {query or 'default'}",
            "items": [
                {
                    "id": generate_simulation_id("item"),
                    "summary": "Simulated memory item",
                    "content": "This is simulated content returned in simulation mode.",
                    "metadata": {"simulation": True},
                    "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "updated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "score": 0.95,
                }
            ],
            "reasoning": "simulation",
            "meta": {
                "mode": "retrieval",
                "format": "inject",
                "limit": 5,
                "query": query,
            },
            "confidence": 1.0,
        }
    
    @staticmethod
    def timeline_walk_result(version_id: str) -> dict:
        """Generate a mock timeline walk result."""
        return {
            "start_version_id": version_id,
            "nodes": [],
            "edges": [],
            "depth": 0,
            "total_visited": 0,
            "truncated": False,
        }
    
    @staticmethod
    def validity_result(version_id: str) -> dict:
        """Generate a mock validity result."""
        return {
            "version_id": version_id,
            "is_valid": True,
            "reason": "Simulation mode - all versions are valid",
            "superseded_by": [],
            "latest_in_chain": version_id,
            "confidence_score": 1.0,
            "age_hours": 0,
        }

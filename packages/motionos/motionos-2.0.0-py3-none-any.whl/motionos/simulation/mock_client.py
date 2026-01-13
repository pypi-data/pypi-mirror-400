"""
MotionOS SDK - Mock Client

A simulation client for offline testing, demos, and CI.
Makes NO network calls - completely deterministic.
"""

import time
import random
from typing import Optional, Dict, Any, List, Union

from motionos.simulation.scenarios import SimulationConfig, MockData, generate_simulation_id
from motionos.errors.base import EngineUnavailableError, RateLimitError


class MockMotionOS:
    """
    Mock MotionOS client for simulation mode.
    
    IMPORTANT: This client must be explicitly enabled.
    It makes ZERO network calls.
    
    Usage:
        from motionos.simulation import MockMotionOS, Scenarios
        
        client = MockMotionOS.create(Scenarios.happy_path())
        
        # All operations work offline
        result = client.ingest("test")
        result = client.retrieve("query")
    """
    
    def __init__(self, config: SimulationConfig):
        if not config.enabled:
            raise ValueError("Cannot create MockMotionOS with enabled=False. Use the real MotionOS client instead.")
        self.config = config
        self.request_count = 0
        self.responses: Dict[str, Any] = config.responses or {}
    
    @classmethod
    def create(cls, config: SimulationConfig) -> "MockMotionOS":
        """Create a mock client with explicit simulation config."""
        return cls(config)
    
    def _simulate_latency(self) -> None:
        """Simulate network latency."""
        latency = self.config.latency_ms / 1000.0
        time.sleep(latency)
    
    def _maybe_error(self) -> None:
        """Maybe throw a simulated error."""
        if random.random() < self.config.error_rate:
            raise EngineUnavailableError("Simulated failure")
    
    def _maybe_rate_limit(self) -> None:
        """Maybe throw rate limit error."""
        self.request_count += 1
        if self.config.rate_limit_after and self.request_count > self.config.rate_limit_after:
            raise RateLimitError("Simulated rate limit", None, 1000)
    
    def reset_rate_limit_counter(self) -> None:
        """Reset rate limit counter."""
        self.request_count = 0
    
    def set_response(self, pattern: str, response: Any) -> None:
        """Add a custom response for a pattern."""
        self.responses[pattern] = response
    
    # ========================================================================
    # Mock Operations
    # ========================================================================
    
    def ingest(self, input: Union[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Mock ingest operation."""
        self._simulate_latency()
        self._maybe_error()
        self._maybe_rate_limit()
        
        raw_text = input if isinstance(input, str) else input.get("raw_text", "")
        return MockData.ingest_result(raw_text[:20] if raw_text else None)
    
    def retrieve(self, input: Union[str, Dict[str, Any]] = "") -> Dict[str, Any]:
        """Mock retrieve operation."""
        self._simulate_latency()
        self._maybe_error()
        self._maybe_rate_limit()
        
        query = input if isinstance(input, str) else input.get("query", "")
        return MockData.retrieval_result(query)
    
    def walk_timeline(self, options: Dict[str, Any]) -> Dict[str, Any]:
        """Mock timeline walk operation."""
        self._simulate_latency()
        self._maybe_error()
        self._maybe_rate_limit()
        
        return MockData.timeline_walk_result(options.get("version_id", "unknown"))
    
    def check_validity(self, version_id: str) -> Dict[str, Any]:
        """Mock validity check operation."""
        self._simulate_latency()
        self._maybe_error()
        self._maybe_rate_limit()
        
        return MockData.validity_result(version_id)
    
    def get_lineage(self, version_id: str) -> Dict[str, Any]:
        """Mock lineage operation."""
        self._simulate_latency()
        self._maybe_error()
        self._maybe_rate_limit()
        
        return {
            "version_id": version_id,
            "ancestors": [],
            "descendants": [],
            "root_version": version_id,
            "current_version": version_id,
            "total_versions": 1,
        }
    
    def list_versions(self, memory_id: str) -> List[Dict[str, Any]]:
        """Mock list versions operation."""
        self._simulate_latency()
        self._maybe_error()
        self._maybe_rate_limit()
        
        return [
            {
                "id": generate_simulation_id("version"),
                "memory_id": memory_id,
                "version": 1,
                "content": "Simulated version content",
                "summary": "Simulated version",
                "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "is_current": True,
            }
        ]
    
    def rollback(self, options: Dict[str, Any]) -> Dict[str, Any]:
        """Mock rollback operation."""
        self._simulate_latency()
        self._maybe_error()
        self._maybe_rate_limit()
        
        return {"ok": True, "current_version_id": options.get("version_id")}
    
    def list_domains(self) -> List[Dict[str, Any]]:
        """Mock list domains operation."""
        self._simulate_latency()
        self._maybe_error()
        self._maybe_rate_limit()
        
        return [
            {
                "name": "default",
                "description": "Default domain (simulation)",
                "default_policy": "default",
                "type_priorities": ["decision", "fact", "preference"],
                "semantic_endpoints_count": 1,
            }
        ]
    
    def list_policies(self) -> List[Dict[str, Any]]:
        """Mock list policies operation."""
        self._simulate_latency()
        self._maybe_error()
        self._maybe_rate_limit()
        
        return [
            {
                "name": "default",
                "description": "Default policy (simulation)",
                "rules": ["balanced_weights"],
                "priority": 1,
            }
        ]
    
    def health(self) -> Dict[str, str]:
        """Mock health check."""
        self._simulate_latency()
        self._maybe_error()
        
        return {"status": "ok", "service": "motionos-simulation"}
    
    def get_config(self) -> Dict[str, Any]:
        """Get mock configuration info."""
        return {
            "base_url": "simulation://mock",
            "project_id": "sim-project",
            "timeout": {"ingest": 12.0, "retrieve": 6.0, "default": 10.0},
            "retry": {"attempts": 2, "backoff_ms": 300},
            "debug": True,
            "sdk_version": "2.0.0",
            "key_type": "secret",
            "simulation_mode": True,
        }

"""
MotionOS SDK - Ingest Builder

Fluent API for building memory ingestion requests.
"""

from typing import Optional, List, Union, Dict, Any
from datetime import datetime

from motionos.ingestion.validator import validate_ingest_options


class IngestBuilder:
    """
    Fluent builder for memory ingestion.
    
    Usage:
        memory = (
            IngestBuilder
            .text("User prefers dark mode")
            .with_type("preference")
            .with_tags(["ui", "settings"])
            .for_agent("ui-agent")
            .build()
        )
    """
    
    def __init__(self):
        self._options: Dict[str, Any] = {"raw_text": ""}
    
    @classmethod
    def text(cls, raw_text: str) -> "IngestBuilder":
        """Start building with raw text content."""
        builder = cls()
        builder._options["raw_text"] = raw_text
        return builder
    
    @classmethod
    def create(cls) -> "IngestBuilder":
        """Start building with empty options."""
        return cls()
    
    def set_text(self, raw_text: str) -> "IngestBuilder":
        """Set the raw text content."""
        self._options["raw_text"] = raw_text
        return self
    
    def with_summary(self, summary: str) -> "IngestBuilder":
        """Set a custom summary."""
        self._options["summary"] = summary
        return self
    
    def for_agent(self, agent_id: str) -> "IngestBuilder":
        """Set the agent ID."""
        self._options["agent_id"] = agent_id
        return self
    
    def in_scope(self, scope: str) -> "IngestBuilder":
        """Set the memory scope."""
        self._options["scope"] = scope
        return self
    
    def project_scoped(self) -> "IngestBuilder":
        """Set as project scope."""
        return self.in_scope("project")
    
    def agent_scoped(self) -> "IngestBuilder":
        """Set as agent scope."""
        return self.in_scope("agent")
    
    def global_scoped(self) -> "IngestBuilder":
        """Set as global scope."""
        return self.in_scope("global")
    
    def with_type(self, memory_type: str) -> "IngestBuilder":
        """Set the memory type."""
        self._options["type"] = memory_type
        return self
    
    def as_decision(self) -> "IngestBuilder":
        """Set as decision type."""
        return self.with_type("decision")
    
    def as_note(self) -> "IngestBuilder":
        """Set as note type."""
        return self.with_type("note")
    
    def as_event(self) -> "IngestBuilder":
        """Set as event type."""
        return self.with_type("event")
    
    def as_preference(self) -> "IngestBuilder":
        """Set as preference type."""
        return self.with_type("preference")
    
    def as_fact(self) -> "IngestBuilder":
        """Set as fact type."""
        return self.with_type("fact")
    
    def as_instruction(self) -> "IngestBuilder":
        """Set as instruction type."""
        return self.with_type("instruction")
    
    def with_tags(self, tags: List[str]) -> "IngestBuilder":
        """Add tags."""
        existing = self._options.get("tags", [])
        self._options["tags"] = existing + tags
        return self
    
    def with_tag(self, tag: str) -> "IngestBuilder":
        """Add a single tag."""
        existing = self._options.get("tags", [])
        self._options["tags"] = existing + [tag]
        return self
    
    def from_source(self, source: str) -> "IngestBuilder":
        """Set the source identifier."""
        self._options["source"] = source
        return self
    
    def at_time(self, event_time: Union[datetime, str]) -> "IngestBuilder":
        """Set the event time."""
        self._options["event_time"] = event_time
        return self
    
    def with_importance(self, importance: float) -> "IngestBuilder":
        """Set importance score (0-1)."""
        self._options["importance"] = importance
        return self
    
    def high_importance(self) -> "IngestBuilder":
        """Set as high importance."""
        return self.with_importance(0.9)
    
    def low_importance(self) -> "IngestBuilder":
        """Set as low importance."""
        return self.with_importance(0.3)
    
    def with_frequency(self, frequency: float) -> "IngestBuilder":
        """Set frequency score (0-1)."""
        self._options["frequency"] = frequency
        return self
    
    def with_recency(self, recency: float) -> "IngestBuilder":
        """Set recency score (0-1)."""
        self._options["recency"] = recency
        return self
    
    def with_edges(self, edges: List[Dict[str, str]]) -> "IngestBuilder":
        """Add timeline edges."""
        existing = self._options.get("edges", [])
        self._options["edges"] = existing + edges
        return self
    
    def caused_by(self, version_id: str) -> "IngestBuilder":
        """Add a causal edge."""
        return self.with_edges([{"to": version_id, "type": "causes"}])
    
    def follows(self, version_id: str) -> "IngestBuilder":
        """Add a follows edge."""
        return self.with_edges([{"to": version_id, "type": "follows"}])
    
    def relates_to(self, version_id: str) -> "IngestBuilder":
        """Add a relates edge."""
        return self.with_edges([{"to": version_id, "type": "relates"}])
    
    def supersedes(self, version_id: str) -> "IngestBuilder":
        """Mark as superseding another memory."""
        return self.with_edges([{"to": version_id, "type": "supersedes"}])
    
    def build(self) -> Dict[str, Any]:
        """Validate and build the options."""
        validate_ingest_options(self._options)
        return self._options.copy()
    
    def get_raw_options(self) -> Dict[str, Any]:
        """Get raw options without validation."""
        return self._options.copy()


def ingest(raw_text: str) -> IngestBuilder:
    """Quick builder function."""
    return IngestBuilder.text(raw_text)


def ingest_decision(text: str) -> IngestBuilder:
    """Create a decision memory."""
    return IngestBuilder.text(text).as_decision()


def ingest_preference(text: str) -> IngestBuilder:
    """Create a preference memory."""
    return IngestBuilder.text(text).as_preference()


def ingest_fact(text: str) -> IngestBuilder:
    """Create a fact memory."""
    return IngestBuilder.text(text).as_fact()


def ingest_event(text: str) -> IngestBuilder:
    """Create an event memory."""
    return IngestBuilder.text(text).as_event()

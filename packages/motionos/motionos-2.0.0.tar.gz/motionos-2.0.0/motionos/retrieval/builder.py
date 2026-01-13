"""
MotionOS SDK - Retrieval Builder

Fluent API for building retrieval queries with intent.
"""

from typing import Optional, List, Union, Dict, Any
from datetime import datetime

from motionos.types.retrieval import (
    RetrieveOptions,
    RetrievalIntent,
    PolicyConfig,
    ScoringWeights,
)
from motionos.retrieval.intent import validate_retrieval_options


class RetrievalBuilder:
    """
    Fluent builder for retrieval queries.
    
    Usage:
        query = (
            RetrievalBuilder
            .query("user preferences")
            .with_intent(RetrievalIntent.DECISION)
            .with_limit(10)
            .explain()
            .build()
        )
    """
    
    def __init__(self):
        self._options: Dict[str, Any] = {}
    
    @classmethod
    def query(cls, query_text: str) -> "RetrievalBuilder":
        """Start building a retrieval query."""
        builder = cls()
        builder._options["query"] = query_text
        return builder
    
    @classmethod
    def create(cls) -> "RetrievalBuilder":
        """Start building a retrieval without query."""
        return cls()
    
    def set_query(self, query: str) -> "RetrievalBuilder":
        """Set the query text."""
        self._options["query"] = query
        return self
    
    def with_intent(self, intent: Union[RetrievalIntent, str]) -> "RetrievalBuilder":
        """Set the retrieval intent."""
        if isinstance(intent, RetrievalIntent):
            self._options["intent"] = intent
        else:
            self._options["intent"] = RetrievalIntent(intent)
        return self
    
    def for_exploration(self) -> "RetrievalBuilder":
        """Set for exploration - broad context gathering."""
        return self.with_intent(RetrievalIntent.EXPLORATION)
    
    def for_answer(self) -> "RetrievalBuilder":
        """Set for answer - precise Q&A recall."""
        return self.with_intent(RetrievalIntent.ANSWER)
    
    def for_decision(self) -> "RetrievalBuilder":
        """Set for decision - authoritative memory."""
        return self.with_intent(RetrievalIntent.DECISION)
    
    def for_timeline(self) -> "RetrievalBuilder":
        """Set for timeline - chronological reasoning."""
        return self.with_intent(RetrievalIntent.TIMELINE)
    
    def for_inject(self) -> "RetrievalBuilder":
        """Set for inject - LLM-ready context."""
        return self.with_intent(RetrievalIntent.INJECT)
    
    def with_format(self, format: str) -> "RetrievalBuilder":
        """Set the output format."""
        self._options["format"] = format
        return self
    
    def with_limit(self, limit: int) -> "RetrievalBuilder":
        """Set the result limit."""
        self._options["limit"] = limit
        return self
    
    def for_agent(self, agent_id: str) -> "RetrievalBuilder":
        """Filter by agent ID."""
        self._options["agent_id"] = agent_id
        return self
    
    def in_scope(self, scope: str) -> "RetrievalBuilder":
        """Filter by scope."""
        self._options["scope"] = scope
        return self
    
    def with_tags(self, tags: List[str]) -> "RetrievalBuilder":
        """Filter by tags."""
        if "filters" not in self._options:
            self._options["filters"] = {}
        self._options["filters"]["tags"] = tags
        return self
    
    def with_types(self, types: List[str]) -> "RetrievalBuilder":
        """Filter by types."""
        if "filters" not in self._options:
            self._options["filters"] = {}
        self._options["filters"]["types"] = types
        return self
    
    def from_source(self, source: str) -> "RetrievalBuilder":
        """Filter by source."""
        if "filters" not in self._options:
            self._options["filters"] = {}
        self._options["filters"]["source"] = source
        return self
    
    def in_time_range(
        self, 
        after_time: Optional[Union[datetime, str]] = None,
        before_time: Optional[Union[datetime, str]] = None,
    ) -> "RetrievalBuilder":
        """Filter by time range."""
        if "filters" not in self._options:
            self._options["filters"] = {}
        if after_time:
            self._options["filters"]["after_time"] = after_time
        if before_time:
            self._options["filters"]["before_time"] = before_time
        return self
    
    def latest_only(self) -> "RetrievalBuilder":
        """Get only latest version of each memory."""
        if "filters" not in self._options:
            self._options["filters"] = {}
        self._options["filters"]["latest_only"] = True
        return self
    
    def from_timeline_version(self, version_id: str) -> "RetrievalBuilder":
        """Start from a timeline version."""
        self._options["timeline_version_id"] = version_id
        return self
    
    def with_policy(self, policy: PolicyConfig) -> "RetrievalBuilder":
        """Configure policy."""
        self._options["policy"] = policy
        return self
    
    def with_policy_preset(self, preset: str) -> "RetrievalBuilder":
        """Use a specific policy preset."""
        if "policy" not in self._options:
            self._options["policy"] = {}
        self._options["policy"]["preset"] = preset
        return self
    
    def with_weights(self, weights: ScoringWeights) -> "RetrievalBuilder":
        """Override scoring weights."""
        if "policy" not in self._options:
            self._options["policy"] = {}
        self._options["policy"]["weights"] = weights
        return self
    
    def with_domain(self, domain: str) -> "RetrievalBuilder":
        """Use a domain adapter."""
        self._options["domain"] = domain
        return self
    
    def explain(self) -> "RetrievalBuilder":
        """Request detailed explanation."""
        self._options["explain"] = True
        return self
    
    def build(self) -> RetrieveOptions:
        """Validate and build the options."""
        validate_retrieval_options(self._options)
        return self._options.copy()
    
    def get_raw_options(self) -> Dict[str, Any]:
        """Get raw options without validation."""
        return self._options.copy()


def retrieve(query: str) -> RetrievalBuilder:
    """Quick builder function."""
    return RetrievalBuilder.query(query)


def retrieve_for_decision(query: str) -> RetrievalBuilder:
    """Create a decision retrieval query."""
    return RetrievalBuilder.query(query).for_decision()


def retrieve_for_exploration(query: str) -> RetrievalBuilder:
    """Create an exploration retrieval query."""
    return RetrievalBuilder.query(query).for_exploration()


def retrieve_for_answer(query: str) -> RetrievalBuilder:
    """Create an answer retrieval query."""
    return RetrievalBuilder.query(query).for_answer()

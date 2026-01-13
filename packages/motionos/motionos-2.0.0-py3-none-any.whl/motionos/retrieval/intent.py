"""
MotionOS SDK - Intent Validation

Validates retrieval intents and options.
"""

from typing import Dict, Any, List, Optional
from motionos.types.retrieval import RetrievalIntent, RETRIEVAL_LIMITS
from motionos.errors.base import ValidationError


# Valid retrieval intents
VALID_INTENTS: List[str] = [
    "exploration",
    "answer",
    "decision",
    "timeline",
    "inject",
]

# Intent descriptions
INTENT_DESCRIPTIONS: Dict[str, str] = {
    "exploration": "Broad context gathering - casts a wide net for related information",
    "answer": "Precise recall - focuses on exact matches for Q&A scenarios",
    "decision": "Authoritative memory - prioritizes high-confidence, decision-relevant memories",
    "timeline": "Chronological reasoning - follows causality and temporal relationships",
    "inject": "LLM-ready context - optimized for prompt injection, balances breadth and relevance",
}


def validate_intent(intent) -> bool:
    """Validate a retrieval intent value."""
    if isinstance(intent, RetrievalIntent):
        return True
    if isinstance(intent, str):
        return intent in VALID_INTENTS
    return False


def validate_scoring_weights(weights: Dict[str, float]) -> bool:
    """Validate scoring weights."""
    if not weights or not isinstance(weights, dict):
        return False
    
    for key in ["semantic", "recency", "importance", "frequency"]:
        if key in weights:
            value = weights[key]
            if not isinstance(value, (int, float)) or value < 0 or value > 1:
                return False
    
    return True


def validate_policy_config(policy: Dict[str, Any]) -> None:
    """Validate policy configuration."""
    if "weights" in policy and policy["weights"]:
        if not validate_scoring_weights(policy["weights"]):
            raise ValidationError(
                "Policy weights must be numbers between 0 and 1",
                "policy.weights"
            )


def validate_retrieval_options(options: Dict[str, Any]) -> None:
    """Validate full retrieval options."""
    # Validate intent if provided
    if "intent" in options and options["intent"] is not None:
        if not validate_intent(options["intent"]):
            raise ValidationError(
                f"Invalid intent: {options['intent']}. Valid intents: {', '.join(VALID_INTENTS)}",
                "intent"
            )
    
    # Validate limit
    if "limit" in options and options["limit"] is not None:
        limit = options["limit"]
        if not isinstance(limit, int):
            raise ValidationError("Limit must be an integer", "limit")
        if limit < RETRIEVAL_LIMITS.MIN_LIMIT:
            raise ValidationError(
                f"Limit must be at least {RETRIEVAL_LIMITS.MIN_LIMIT}",
                "limit"
            )
        if limit > RETRIEVAL_LIMITS.MAX_LIMIT:
            raise ValidationError(
                f"Limit cannot exceed {RETRIEVAL_LIMITS.MAX_LIMIT}",
                "limit"
            )
    
    # Validate query length
    if "query" in options and options["query"] is not None:
        query = options["query"]
        if isinstance(query, str) and len(query) > RETRIEVAL_LIMITS.MAX_QUERY_LENGTH:
            raise ValidationError(
                f"Query too long (max {RETRIEVAL_LIMITS.MAX_QUERY_LENGTH} characters)",
                "query"
            )
    
    # Validate policy if provided
    if "policy" in options and options["policy"]:
        validate_policy_config(options["policy"])
    
    # Validate filters
    if "filters" in options and options["filters"]:
        filters = options["filters"]
        if "tags" in filters and filters["tags"] is not None:
            if not isinstance(filters["tags"], list):
                raise ValidationError("filters.tags must be a list", "filters.tags")
        if "types" in filters and filters["types"] is not None:
            if not isinstance(filters["types"], list):
                raise ValidationError("filters.types must be a list", "filters.types")


def get_recommended_policy(intent: str) -> str:
    """Get recommended policy preset for an intent."""
    mapping = {
        "exploration": "exploration",
        "answer": "default",
        "decision": "decision",
        "timeline": "timeline",
        "inject": "default",
    }
    return mapping.get(intent, "default")


def suggest_intent(query: str) -> str:
    """
    Suggest intent from query (simple heuristics).
    
    Note: Actual intent detection happens server-side.
    """
    lower = query.lower()
    
    # Decision-related
    if any(word in lower for word in ["should", "decide", "choice"]):
        return "decision"
    
    # Timeline-related
    if any(word in lower for word in ["when", "history", "sequence"]):
        return "timeline"
    
    # Answer-related
    if any(phrase in lower for phrase in ["what is", "who is", "how to"]):
        return "answer"
    
    # Exploration-related
    if any(phrase in lower for phrase in ["tell me about", "explain", "overview"]):
        return "exploration"
    
    # Default to inject
    return "inject"

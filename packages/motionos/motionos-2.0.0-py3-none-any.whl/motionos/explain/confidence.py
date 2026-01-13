"""
MotionOS SDK - Confidence Scoring

Utilities for working with confidence scores.
"""

from typing import Dict, Any, List


# Confidence level thresholds
CONFIDENCE_THRESHOLDS = {
    "high": 0.8,
    "medium": 0.5,
    "low": 0.3,
}


def get_confidence_level(score: float) -> str:
    """Get confidence level from a score."""
    if score >= CONFIDENCE_THRESHOLDS["high"]:
        return "high"
    if score >= CONFIDENCE_THRESHOLDS["medium"]:
        return "medium"
    if score >= CONFIDENCE_THRESHOLDS["low"]:
        return "low"
    return "very_low"


def describe_confidence(score: float) -> str:
    """Get human-readable confidence description."""
    level = get_confidence_level(score)
    percentage = score * 100
    
    descriptions = {
        "high": f"High confidence ({percentage:.0f}%) - results are likely relevant",
        "medium": f"Medium confidence ({percentage:.0f}%) - results may need verification",
        "low": f"Low confidence ({percentage:.0f}%) - consider refining your query",
        "very_low": f"Very low confidence ({percentage:.0f}%) - results may not be relevant",
    }
    
    return descriptions.get(level, f"Unknown confidence ({percentage:.0f}%)")


def calculate_aggregate_confidence(selections: List[Dict[str, Any]]) -> float:
    """Calculate aggregate confidence from selections."""
    if not selections:
        return 0.0
    
    # Weighted average: higher-ranked items contribute more
    weighted_sum = 0.0
    total_weight = 0.0
    
    for i, sel in enumerate(selections):
        weight = 1 / (i + 1)  # Rank-based weight
        weighted_sum += sel.get("final_score", 0) * weight
        total_weight += weight
    
    return weighted_sum / total_weight if total_weight > 0 else 0.0


def identify_confidence_factors(explanation: Dict[str, Any]) -> List[str]:
    """Identify confidence factors from an explanation."""
    factors: List[str] = []
    
    # Intent confidence
    query_analysis = explanation.get("query_analysis", {})
    intent_confidence = query_analysis.get("intent_confidence", 0)
    if intent_confidence > 0.8:
        factors.append("Clear query intent detected")
    elif intent_confidence < 0.4:
        factors.append("Ambiguous query intent")
    
    # Result count
    returned = explanation.get("items_returned", 0)
    considered = explanation.get("items_considered", 0)
    if returned == 0:
        factors.append("No results found")
    elif returned < 3 and considered > 10:
        factors.append("Few results matched criteria")
    elif returned > 10:
        factors.append("Many relevant results found")
    
    # Suppression rate
    suppressed = explanation.get("items_suppressed", 0)
    if suppressed > returned * 2:
        factors.append("Many items filtered by policy")
    
    # Selection score distribution
    selections = explanation.get("selections", [])
    if selections:
        top_score = selections[0].get("final_score", 0)
        last_score = selections[-1].get("final_score", 0) if len(selections) > 1 else top_score
        
        if top_score > 0.9:
            factors.append("Top result has very high relevance")
        if top_score - last_score < 0.1 and len(selections) > 3:
            factors.append("Results have similar relevance scores")
    
    return factors


def is_confidence_sufficient(score: float, use_case: str) -> bool:
    """Check if confidence is sufficient for a given use case."""
    thresholds = {
        "decision": CONFIDENCE_THRESHOLDS["high"],
        "exploration": CONFIDENCE_THRESHOLDS["low"],
        "injection": CONFIDENCE_THRESHOLDS["medium"],
    }
    
    return score >= thresholds.get(use_case, CONFIDENCE_THRESHOLDS["medium"])


def get_confidence_improvement_suggestions(explanation: Dict[str, Any]) -> List[str]:
    """Get confidence improvement suggestions."""
    suggestions: List[str] = []
    confidence = explanation.get("overall_confidence", 0)
    
    if confidence >= CONFIDENCE_THRESHOLDS["high"]:
        return []  # No improvements needed
    
    # Low intent confidence
    query_analysis = explanation.get("query_analysis", {})
    if query_analysis.get("intent_confidence", 0) < 0.5:
        suggestions.append("Try using more specific query terms")
        suggestions.append('Explicitly specify your intent (e.g., "for decision making...")')
    
    # Few results
    if explanation.get("items_returned", 0) < 3:
        suggestions.append("Broaden your query to find more relevant memories")
        suggestions.append("Try different keywords or synonyms")
    
    # High suppression
    if explanation.get("items_suppressed", 0) > explanation.get("items_returned", 0):
        suggestions.append("Adjust filters to see more results")
        suggestions.append("Try a different policy preset")
    
    return suggestions

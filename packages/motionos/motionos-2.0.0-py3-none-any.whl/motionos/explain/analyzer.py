"""
MotionOS SDK - Explanation Analyzer

Tools for analyzing and extracting insights from explanations.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field


@dataclass
class ExplanationAnalysis:
    """Summary of an explanation analysis."""
    items_considered: int
    items_returned: int
    items_suppressed: int
    dominant_signal: str
    average_confidence: float
    policy_used: str
    detected_intent: Optional[str]
    insights: List[str] = field(default_factory=list)


def analyze_explanation(explanation: Dict[str, Any]) -> ExplanationAnalysis:
    """Analyze a retrieval explanation."""
    selections = explanation.get("selections", [])
    suppressions = explanation.get("suppressions", [])
    
    # Find dominant signal across all selections
    signal_counts: Dict[str, int] = {}
    for sel in selections:
        signal = sel.get("dominant_signal", "unknown")
        signal_counts[signal] = signal_counts.get(signal, 0) + 1
    
    dominant_signal = "unknown"
    if signal_counts:
        dominant_signal = max(signal_counts.items(), key=lambda x: x[1])[0]
    
    # Calculate average confidence
    total_confidence = sum(sel.get("final_score", 0) for sel in selections)
    average_confidence = total_confidence / len(selections) if selections else 0
    
    # Generate insights
    insights = _generate_insights(explanation, selections, suppressions, dominant_signal)
    
    # Query analysis
    query_analysis = explanation.get("query_analysis", {})
    detected_intent = query_analysis.get("detected_intent")
    
    return ExplanationAnalysis(
        items_considered=explanation.get("items_considered", 0),
        items_returned=explanation.get("items_returned", len(selections)),
        items_suppressed=explanation.get("items_suppressed", len(suppressions)),
        dominant_signal=dominant_signal,
        average_confidence=average_confidence,
        policy_used=explanation.get("policy_used", "default"),
        detected_intent=detected_intent,
        insights=insights,
    )


def _generate_insights(
    explanation: Dict[str, Any],
    selections: List[Dict[str, Any]],
    suppressions: List[Dict[str, Any]],
    dominant_signal: str,
) -> List[str]:
    """Generate human-readable insights from an explanation."""
    insights: List[str] = []
    
    # Policy insight
    if explanation.get("policy_used"):
        insights.append(f'Applied "{explanation["policy_used"]}" policy for this retrieval')
    
    # Intent insight
    query_analysis = explanation.get("query_analysis", {})
    if query_analysis.get("detected_intent"):
        intent = query_analysis["detected_intent"]
        confidence = query_analysis.get("intent_confidence", 0)
        if confidence > 0.7:
            insights.append(f'High confidence ({confidence * 100:.0f}%) "{intent}" intent detected')
        else:
            insights.append(f'"{intent}" intent detected with moderate confidence')
    
    # Dominant signal insight
    if dominant_signal != "unknown":
        insights.append(f"Results were primarily driven by {dominant_signal} matching")
    
    # Suppression insight
    if suppressions:
        rules = list(set(s.get("suppression_rule") for s in suppressions if s.get("suppression_rule")))
        insights.append(f"{len(suppressions)} items filtered out by: {', '.join(rules)}")
    
    # Confidence insight
    overall_confidence = explanation.get("overall_confidence", 0)
    if overall_confidence > 0.8:
        insights.append("High confidence in result quality")
    elif overall_confidence < 0.5:
        insights.append("Low confidence - consider refining your query")
    
    return insights


def get_top_reasons(selection: Dict[str, Any], limit: int = 3) -> List[Dict[str, Any]]:
    """Get the top reasons for a selection."""
    reasons = selection.get("top_reasons", [])
    sorted_reasons = sorted(reasons, key=lambda r: r.get("contribution", 0), reverse=True)
    return sorted_reasons[:limit]


def find_suppression_reason(
    explanation: Dict[str, Any],
    item_id: str,
) -> Optional[Dict[str, Any]]:
    """Find why a specific item was suppressed."""
    for sup in explanation.get("suppressions", []):
        if sup.get("item_id") == item_id:
            return sup
    return None


def find_selection_explanation(
    explanation: Dict[str, Any],
    item_id: str,
) -> Optional[Dict[str, Any]]:
    """Find why a specific item was selected."""
    for sel in explanation.get("selections", []):
        if sel.get("item_id") == item_id:
            return sel
    return None


def is_high_confidence(explanation: Dict[str, Any]) -> bool:
    """Check if results are high confidence."""
    return explanation.get("overall_confidence", 0) >= 0.7


def has_strong_intent(explanation: Dict[str, Any]) -> bool:
    """Check if query intent was clearly detected."""
    query_analysis = explanation.get("query_analysis", {})
    return query_analysis.get("intent_confidence", 0) >= 0.7


def get_applied_filters(explanation: Dict[str, Any]) -> List[str]:
    """Get the effective filter criteria that were applied."""
    filters: List[str] = []
    query_analysis = explanation.get("query_analysis", {})
    
    expected_types = query_analysis.get("expected_types", [])
    if expected_types:
        filters.append(f"types: {', '.join(expected_types)}")
    
    return filters

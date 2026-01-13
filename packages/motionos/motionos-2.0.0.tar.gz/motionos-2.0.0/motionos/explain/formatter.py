"""
MotionOS SDK - Explanation Formatter

Format explanations for human consumption.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass


@dataclass
class FormatOptions:
    """Format options for explanation output."""
    verbose: bool = False
    max_selections: int = 5
    max_suppressions: int = 3
    style: str = "text"  # "text", "markdown", "json"


def format_explanation(
    explanation: Dict[str, Any],
    options: Optional[FormatOptions] = None,
) -> str:
    """Format a retrieval explanation as human-readable text."""
    opts = options or FormatOptions()
    
    if opts.style == "json":
        import json
        return json.dumps(explanation, indent=2)
    
    lines: List[str] = []
    is_markdown = opts.style == "markdown"
    h1 = "# " if is_markdown else ""
    h2 = "## " if is_markdown else ""
    bullet = "- " if is_markdown else "• "
    
    # Header
    lines.append(f"{h1}Retrieval Explanation")
    lines.append("")
    
    # Summary
    if explanation.get("summary"):
        lines.append(explanation["summary"])
        lines.append("")
    
    # Query Analysis
    query_analysis = explanation.get("query_analysis", {})
    if query_analysis:
        lines.append(f"{h2}Query Analysis")
        if query_analysis.get("original_query"):
            lines.append(f'{bullet}Query: "{query_analysis["original_query"]}"')
        if query_analysis.get("detected_intent"):
            confidence = query_analysis.get("intent_confidence", 0)
            lines.append(f'{bullet}Intent: {query_analysis["detected_intent"]} ({confidence * 100:.0f}% confidence)')
        key_terms = query_analysis.get("key_terms", [])
        if key_terms:
            lines.append(f"{bullet}Key terms: {', '.join(key_terms)}")
        lines.append("")
    
    # Policy & Confidence
    lines.append(f"{h2}Configuration")
    lines.append(f"{bullet}Policy: {explanation.get('policy_used', 'default')}")
    if explanation.get("policy_reason"):
        lines.append(f"{bullet}Reason: {explanation['policy_reason']}")
    confidence = explanation.get("overall_confidence", 0)
    lines.append(f"{bullet}Confidence: {confidence * 100:.0f}%")
    lines.append("")
    
    # Statistics
    lines.append(f"{h2}Results")
    lines.append(f"{bullet}Considered: {explanation.get('items_considered', 0)}")
    lines.append(f"{bullet}Returned: {explanation.get('items_returned', 0)}")
    lines.append(f"{bullet}Suppressed: {explanation.get('items_suppressed', 0)}")
    lines.append("")
    
    # Selections
    selections = explanation.get("selections", [])[:opts.max_selections]
    if selections:
        lines.append(f"{h2}Selected Items")
        for sel in selections:
            lines.append(_format_selection(sel, bullet, opts.verbose))
        lines.append("")
    
    # Suppressions (verbose only)
    if opts.verbose:
        suppressions = explanation.get("suppressions", [])[:opts.max_suppressions]
        if suppressions:
            lines.append(f"{h2}Suppressed Items")
            for sup in suppressions:
                lines.append(_format_suppression(sup, bullet))
            lines.append("")
    
    # Confidence factors (verbose only)
    if opts.verbose:
        factors = explanation.get("confidence_factors", [])
        if factors:
            lines.append(f"{h2}Confidence Factors")
            for factor in factors:
                lines.append(f"{bullet}{factor}")
    
    return "\n".join(lines)


def _format_selection(sel: Dict[str, Any], bullet: str, verbose: bool) -> str:
    """Format a single selection explanation."""
    score = sel.get("final_score", 0) * 100
    rank = sel.get("rank", 0)
    summary = sel.get("summary") or sel.get("item_id", "unknown")
    
    line = f"{bullet}#{rank} [{score:.1f}%] - {summary}"
    
    if verbose:
        reasons = sel.get("top_reasons", [])[:3]
        for reason in reasons:
            line += f"\n  {bullet}{reason.get('signal')}: {reason.get('impact')}"
    
    return line


def _format_suppression(sup: Dict[str, Any], bullet: str) -> str:
    """Format a single suppression explanation."""
    item_id = sup.get("item_id", "unknown")
    reason = sup.get("reason", "unknown")
    rule = sup.get("suppression_rule", "unknown")
    return f"{bullet}{item_id}: {reason} ({rule})"


def summarize_explanation(explanation: Dict[str, Any]) -> str:
    """Create a brief one-line summary of an explanation."""
    returned = explanation.get("items_returned", 0)
    considered = explanation.get("items_considered", 0)
    confidence = explanation.get("overall_confidence", 0) * 100
    policy = explanation.get("policy_used", "default")
    
    query_analysis = explanation.get("query_analysis", {})
    intent = query_analysis.get("detected_intent")
    
    summary = f"Returned {returned}/{considered} items"
    summary += f" ({confidence:.0f}% confidence)"
    summary += f" using {policy} policy"
    if intent:
        summary += f" for {intent} intent"
    
    return summary


def format_for_logging(explanation: Dict[str, Any]) -> Dict[str, Any]:
    """Format explanation for logging (compact)."""
    query_analysis = explanation.get("query_analysis", {})
    return {
        "policy": explanation.get("policy_used"),
        "intent": query_analysis.get("detected_intent"),
        "confidence": explanation.get("overall_confidence"),
        "returned": explanation.get("items_returned"),
        "suppressed": explanation.get("items_suppressed"),
    }

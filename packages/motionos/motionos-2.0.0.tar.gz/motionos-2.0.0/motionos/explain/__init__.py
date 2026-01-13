"""
MotionOS SDK - Explainability Package

Tools for understanding and presenting retrieval explanations.
"""

from motionos.explain.analyzer import (
    ExplanationAnalysis,
    analyze_explanation,
    get_top_reasons,
    find_suppression_reason,
    find_selection_explanation,
    is_high_confidence,
)
from motionos.explain.formatter import (
    format_explanation,
    summarize_explanation,
    format_for_logging,
)
from motionos.explain.confidence import (
    CONFIDENCE_THRESHOLDS,
    get_confidence_level,
    describe_confidence,
    calculate_aggregate_confidence,
    get_confidence_improvement_suggestions,
)

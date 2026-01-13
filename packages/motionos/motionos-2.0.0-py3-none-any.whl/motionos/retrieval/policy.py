"""
MotionOS SDK - Policy Configuration

Policy presets and configuration helpers.
"""

from typing import Dict, Any, Optional


class PolicyPresets:
    """Pre-built policy configurations."""
    
    @staticmethod
    def default() -> Dict[str, Any]:
        """Default balanced policy."""
        return {"preset": "default"}
    
    @staticmethod
    def decision() -> Dict[str, Any]:
        """Decision-making policy - prioritizes importance and authority."""
        return {
            "preset": "decision",
            "weights": {
                "semantic": 0.3,
                "importance": 0.4,
                "recency": 0.2,
                "frequency": 0.1,
            },
        }
    
    @staticmethod
    def timeline() -> Dict[str, Any]:
        """Timeline policy - prioritizes recency and causality."""
        return {
            "preset": "timeline",
            "weights": {
                "semantic": 0.2,
                "importance": 0.2,
                "recency": 0.5,
                "frequency": 0.1,
            },
        }
    
    @staticmethod
    def exploration() -> Dict[str, Any]:
        """Exploration policy - prioritizes semantic breadth."""
        return {
            "preset": "exploration",
            "weights": {
                "semantic": 0.5,
                "importance": 0.2,
                "recency": 0.2,
                "frequency": 0.1,
            },
        }
    
    @staticmethod
    def audit() -> Dict[str, Any]:
        """Audit policy - equal weights, no suppression."""
        return {
            "preset": "audit",
            "weights": {
                "semantic": 0.25,
                "importance": 0.25,
                "recency": 0.25,
                "frequency": 0.25,
            },
        }
    
    @staticmethod
    def custom(weights: Dict[str, float]) -> Dict[str, Any]:
        """Custom policy with specific weights."""
        return {"weights": weights}
    
    @staticmethod
    def auto_detect() -> Dict[str, Any]:
        """Auto-detect intent from query."""
        return {"auto_detect": True}


def merge_with_preset(preset: str, custom_weights: Dict[str, float]) -> Dict[str, Any]:
    """Merge custom weights with a preset."""
    preset_methods = {
        "default": PolicyPresets.default,
        "decision": PolicyPresets.decision,
        "timeline": PolicyPresets.timeline,
        "exploration": PolicyPresets.exploration,
        "audit": PolicyPresets.audit,
    }
    
    base_policy = preset_methods.get(preset, PolicyPresets.default)()
    base_weights = base_policy.get("weights", {})
    
    return {
        **base_policy,
        "weights": {**base_weights, **custom_weights},
    }


def normalize_weights(weights: Dict[str, float]) -> Dict[str, float]:
    """Normalize weights to sum to 1."""
    values = [
        weights.get("semantic", 0),
        weights.get("recency", 0),
        weights.get("importance", 0),
        weights.get("frequency", 0),
    ]
    
    total = sum(values)
    if total == 0:
        return {
            "semantic": 0.25,
            "recency": 0.25,
            "importance": 0.25,
            "frequency": 0.25,
        }
    
    return {
        "semantic": weights.get("semantic", 0) / total,
        "recency": weights.get("recency", 0) / total,
        "importance": weights.get("importance", 0) / total,
        "frequency": weights.get("frequency", 0) / total,
    }


def describe_policy_config(policy: Dict[str, Any]) -> str:
    """Get human-readable description of a policy."""
    if policy.get("auto_detect"):
        return "Auto-detect intent from query and apply appropriate policy"
    
    preset = policy.get("preset")
    if preset:
        descriptions = {
            "default": "Balanced scoring across all factors",
            "decision": "Prioritizes authoritative and important memories",
            "timeline": "Prioritizes recent events and causality",
            "exploration": "Broad semantic matching for context gathering",
            "audit": "Equal weights for inspection and debugging",
        }
        return descriptions.get(preset, f"Custom policy: {preset}")
    
    weights = policy.get("weights")
    if weights:
        parts = []
        if weights.get("semantic"):
            parts.append(f"semantic: {weights['semantic'] * 100:.0f}%")
        if weights.get("recency"):
            parts.append(f"recency: {weights['recency'] * 100:.0f}%")
        if weights.get("importance"):
            parts.append(f"importance: {weights['importance'] * 100:.0f}%")
        if weights.get("frequency"):
            parts.append(f"frequency: {weights['frequency'] * 100:.0f}%")
        return f"Custom weights: {', '.join(parts)}"
    
    return "Default policy"

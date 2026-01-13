"""
MotionOS SDK - Test Fixtures

Predefined test data fixtures.
"""

from typing import Dict, Any
import time
import random
import string


# Sample memory content for testing
sample_memories = {
    "decision": {
        "raw_text": "User decided to upgrade their subscription plan from Basic to Pro",
        "type": "decision",
        "metadata": {"source": "test", "category": "subscription"},
    },
    "preference": {
        "raw_text": "User prefers dark mode and reduced motion",
        "type": "preference",
        "metadata": {"source": "test", "category": "ui"},
    },
    "fact": {
        "raw_text": "User account was created on 2024-01-15",
        "type": "fact",
        "metadata": {"source": "test", "category": "account"},
    },
    "event": {
        "raw_text": "User completed onboarding tutorial",
        "type": "event",
        "metadata": {"source": "test", "category": "onboarding"},
    },
}

# Sample queries for testing
sample_queries = {
    "simple": "What does the user prefer for UI settings?",
    "decisions": "What decisions has the user made about their subscription?",
    "timeline": "What happened during onboarding?",
    "complex": "Based on user preferences and past decisions, what plan would suit them?",
}

# Sample API keys for testing (NOT REAL)
test_api_keys = {
    "secret": "sb_secret_test_mock_key_for_testing_only_12345",
    "publishable": "sb_publishable_test_mock_key_for_testing_only_12345",
    "invalid": "invalid_key_format",
}

# Sample project IDs
test_project_ids = {
    "valid": "test-project-id",
    "uuid": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "invalid": "",
}


def create_test_config(overrides: Dict[str, Any] = None) -> Dict[str, Any]:
    """Create a test configuration."""
    config = {
        "api_key": test_api_keys["secret"],
        "project_id": test_project_ids["valid"],
        "debug": True,
    }
    if overrides:
        config.update(overrides)
    return config


def generate_test_id(prefix: str = "test") -> str:
    """Generate a random test ID."""
    random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    return f"{prefix}_{int(time.time())}_{random_suffix}"

"""
MotionOS SDK - Complete Usage Example

This example demonstrates all major SDK features.
"""

import os
import time
import asyncio
from motionos import MotionOS
from motionos.simulation import MockMotionOS, Scenarios
from motionos.retrieval import RetrievalBuilder
from motionos.ingestion import IngestBuilder
from motionos.timeline import TimelineClient


# ============================================================================
# CONFIGURATION
# ============================================================================

def create_client():
    """Create a real client (requires API key)."""
    return MotionOS(
        api_key=os.environ.get("MOTIONOS_API_KEY", ""),
        project_id=os.environ.get("MOTIONOS_PROJECT_ID", ""),
    )


def create_mock_client():
    """Create a mock client for testing."""
    return MockMotionOS.create(Scenarios.happy_path())


# ============================================================================
# MEMORY INGESTION
# ============================================================================

def ingest_examples(client):
    print("\n=== Memory Ingestion ===\n")
    
    # Simple ingestion
    simple = client.ingest("User enabled dark mode")
    print(f"Simple ingest: {simple['id']}")
    
    # Typed ingestion
    typed = client.ingest({
        "raw_text": "User upgraded to Pro plan on 2024-01-15",
        "type": "decision",
        "metadata": {
            "category": "subscription",
            "value": "pro",
        },
    })
    print(f"Typed ingest: {typed['id']}")


# ============================================================================
# MEMORY RETRIEVAL
# ============================================================================

def retrieval_examples(client):
    print("\n=== Memory Retrieval ===\n")
    
    # Simple query
    simple = client.retrieve("What are the user preferences?")
    print(f"Context: {simple['context'][:100]}...")
    
    # With options
    with_intent = client.retrieve({
        "query": "What subscription plan does the user have?",
        "limit": 3,
    })
    print(f"Items found: {len(with_intent.get('items', []))}")


# ============================================================================
# SIMULATION MODE
# ============================================================================

def simulation_examples():
    print("\n=== Simulation Mode ===\n")
    
    # Happy path - everything works
    happy = MockMotionOS.create(Scenarios.happy_path())
    result1 = happy.ingest("Test data")
    print(f"Happy path result: {result1['id']}")
    
    # Slow network simulation
    slow = MockMotionOS.create(Scenarios.slow_network())
    start = time.time()
    slow.retrieve("test")
    elapsed = time.time() - start
    print(f"Slow request took: {elapsed:.2f}s")
    
    # Rate limiting simulation
    limited = MockMotionOS.create(Scenarios.rate_limited(3))
    for i in range(5):
        try:
            limited.ingest(f"Test {i}")
            print(f"Request {i}: OK")
        except Exception as e:
            print(f"Request {i}: Rate limited")


# ============================================================================
# ERROR HANDLING
# ============================================================================

def error_handling_examples():
    print("\n=== Error Handling ===\n")
    
    unstable = MockMotionOS.create(Scenarios.unstable(0.5))
    
    for i in range(5):
        try:
            unstable.ingest("Test")
            print(f"Attempt {i + 1}: Success")
        except Exception as e:
            print(f"Attempt {i + 1}: {type(e).__name__}")


# ============================================================================
# RUN ALL EXAMPLES
# ============================================================================

def main():
    print("MotionOS SDK - Complete Example\n")
    print("================================")
    
    # Use mock client for examples
    simulation_examples()
    error_handling_examples()
    
    # With mock client
    mock = create_mock_client()
    ingest_examples(mock)
    retrieval_examples(mock)
    
    print("\n================================")
    print("Examples complete!")


if __name__ == "__main__":
    main()

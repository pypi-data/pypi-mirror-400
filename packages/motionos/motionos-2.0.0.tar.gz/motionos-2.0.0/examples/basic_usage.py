"""
Basic usage examples for MotionOS Python SDK.

This demonstrates simple ingest and retrieve operations.
"""

from motionos import MotionOS

# Initialize client
client = MotionOS(
    api_key="sb_secret_xxx",  # Replace with your API key
    project_id="proj-123",  # Replace with your project ID
)

# Example 1: Simple ingest
print("Example 1: Ingesting memory...")
result = client.ingest("User prefers dark mode")
print(f"Ingested memory: {result.id}")
print(f"Summary: {result.summary}")
print(f"Version ID: {result.version_id}")

# Example 2: Ingest with options
print("\nExample 2: Ingesting with options...")
result = client.ingest(
    {
        "raw_text": "User loves Python and machine learning",
        "agent_id": "assistant-1",
        "tags": ["preferences", "programming"],
        "type": "preference",
    }
)
print(f"Ingested: {result.id}")

# Example 3: Retrieve context
print("\nExample 3: Retrieving context...")
ctx = client.retrieve("user preferences")
print(f"Context: {ctx.context}")
print(f"Reasoning: {ctx.reasoning}")
print(f"Items found: {len(ctx.items)}")

# Example 4: Retrieve with filters
print("\nExample 4: Retrieving with filters...")
result = client.retrieve(
    {
        "query": "programming",
        "tags": ["programming"],
        "mode": "raw",
        "limit": 5,
    }
)
print(f"Found {len(result.items)} items")
for item in result.items:
    print(f"  - {item.summary} (score: {item.score:.3f})")

# Example 5: Health check
print("\nExample 5: Health check...")
health = client.health()
print(f"Health status: {health}")


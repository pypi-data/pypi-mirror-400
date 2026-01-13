"""
Async usage examples for MotionOS Python SDK.

This demonstrates async operations using AsyncMotionOS.
"""

import asyncio
from motionos import AsyncMotionOS


async def main():
    # Initialize async client
    async with AsyncMotionOS(
        api_key="sb_secret_xxx",  # Replace with your API key
        project_id="proj-123",  # Replace with your project ID
    ) as client:
        # Example 1: Async ingest
        print("Example 1: Async ingest...")
        result = await client.ingest("User prefers async operations")
        print(f"Ingested: {result.id}")

        # Example 2: Async retrieve
        print("\nExample 2: Async retrieve...")
        ctx = await client.retrieve("user preferences")
        print(f"Context: {ctx.context}")

        # Example 3: Batch ingest (parallel)
        print("\nExample 3: Batch ingest (parallel)...")
        from motionos.types import BatchIngestOptions

        batch_result = await client.batch_ingest(
            BatchIngestOptions(
                items=[
                    {"raw_text": "Memory 1", "tags": ["async"]},
                    {"raw_text": "Memory 2", "tags": ["async"]},
                    {"raw_text": "Memory 3", "tags": ["async"]},
                ]
            )
        )
        print(f"Batch ingest completed: {len(batch_result.results)} items")
        for i, r in enumerate(batch_result.results):
            if r.id:
                print(f"  Item {i+1}: Success - {r.id}")
            elif r.error:
                print(f"  Item {i+1}: Error - {r.error}")


if __name__ == "__main__":
    asyncio.run(main())


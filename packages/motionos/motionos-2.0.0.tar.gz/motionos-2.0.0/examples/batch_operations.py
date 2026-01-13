"""
Batch operations examples for MotionOS Python SDK.

This demonstrates batch ingest operations.
"""

from motionos import MotionOS
from motionos.types import BatchIngestOptions

client = MotionOS(api_key="sb_secret_xxx", project_id="proj-123")

# Example 1: Batch ingest with default chunk size
print("Example 1: Batch ingest...")
items = [
    {"raw_text": f"Memory item {i}", "tags": ["batch"], "type": "example"}
    for i in range(1, 21)  # 20 items
]

batch_result = client.batch_ingest(BatchIngestOptions(items=items, chunk_size=10))

print(f"Total items: {len(batch_result.results)}")
success_count = sum(1 for r in batch_result.results if r.id)
error_count = sum(1 for r in batch_result.results if r.error)

print(f"Success: {success_count}")
print(f"Errors: {error_count}")

# Show errors if any
for i, r in enumerate(batch_result.results):
    if r.error:
        print(f"  Item {i+1} error: {r.error}")


# Example 2: Async batch ingest (parallel processing)
print("\nExample 2: Async batch ingest...")
import asyncio
from motionos import AsyncMotionOS


async def async_batch_example():
    async with AsyncMotionOS(api_key="sb_secret_xxx", project_id="proj-123") as client:
        items = [
            {"raw_text": f"Async memory {i}", "tags": ["async", "batch"]}
            for i in range(1, 6)
        ]

        batch_result = await client.batch_ingest(BatchIngestOptions(items=items))
        print(f"Async batch completed: {len(batch_result.results)} items")


asyncio.run(async_batch_example())


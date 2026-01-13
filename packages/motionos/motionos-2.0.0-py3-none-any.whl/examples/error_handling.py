"""
Error handling examples for MotionOS Python SDK.

This demonstrates how to handle various error scenarios.
"""

from motionos import MotionOS
from motionos.errors import (
    MotionOSError,
    InvalidAPIKeyError,
    RateLimitError,
    NetworkError,
    is_retryable,
)

client = MotionOS(api_key="sb_secret_xxx", project_id="proj-123")


# Example 1: Basic error handling
print("Example 1: Basic error handling...")
try:
    result = client.ingest("Test memory")
except MotionOSError as e:
    print(f"Error: {e.message} (code: {e.code})")
    if e.http_status:
        print(f"HTTP Status: {e.http_status}")
    if e.request_id:
        print(f"Request ID: {e.request_id}")


# Example 2: Specific error handling
print("\nExample 2: Specific error handling...")
try:
    result = client.ingest("Test")
except InvalidAPIKeyError:
    print("Invalid API key - check your credentials")
except RateLimitError as e:
    print("Rate limit exceeded - retry later")
    # SDK automatically handles retries, but you can add custom logic
except NetworkError:
    print("Network error - check your connection")
except MotionOSError as e:
    print(f"Other error: {e.message}")


# Example 3: Check if error is retryable
print("\nExample 3: Retryable error check...")
try:
    result = client.retrieve("test query")
except MotionOSError as e:
    if is_retryable(e):
        print(f"Retryable error: {e.code}")
        # Implement custom retry logic if needed
    else:
        print(f"Non-retryable error: {e.code}")


# Example 4: Handle rate limits with custom backoff
print("\nExample 4: Custom rate limit handling...")
import time

max_retries = 3
for attempt in range(max_retries):
    try:
        result = client.ingest("Test memory")
        break
    except RateLimitError as e:
        if attempt < max_retries - 1:
            wait_time = (attempt + 1) * 2  # Exponential backoff
            print(f"Rate limited, waiting {wait_time}s...")
            time.sleep(wait_time)
        else:
            print("Max retries reached")
            raise


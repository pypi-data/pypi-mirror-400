"""
MotionOS SDK - Main Client (Sync)

Provides synchronous client for interacting with MotionOS API.
"""

import json
import logging
import time
from typing import Any, Dict, List, Optional, Union
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from motionos.errors import (
    MotionOSError,
    create_motionos_error,
    is_retryable,
    InvalidAPIKeyError,
    InvalidRequestError,
    ForbiddenError,
)
from motionos.security import validate_api_key, validate_operation, ApiKeyType
from motionos.types import (
    IngestInput,
    IngestOptions,
    IngestResult,
    RetrieveInput,
    RetrieveOptions,
    RetrievalResult,
    RollbackOptions,
    RollbackResult,
    MemoryItem,
    BatchIngestOptions,
    BatchIngestResult,
    BatchIngestResultItem,
    VersionInfo,
    SDKConfig,
    TimeoutConfig,
    RetryConfig,
)
from motionos.utils import (
    generate_request_id,
    exponential_backoff,
    sanitize_for_logging,
    remove_undefined,
    chunk_list,
)

logger = logging.getLogger("motionos")
SDK_VERSION = "1.0.0"


class MotionOS:
    """
    MotionOS SDK Client (Synchronous)

    Provides a clean interface for interacting with MotionOS API.

    Example:
        ```python
        from motionos import MotionOS

        client = MotionOS(
            api_key="sb_secret_xxx",
            project_id="proj-123"
        )

        # Simple ingest
        result = client.ingest("User prefers dark mode")

        # Retrieve context
        ctx = client.retrieve("user preferences")
        print(ctx.context)  # Ready for LLM
        ```
    """

    def __init__(
        self,
        api_key: str,
        project_id: str,
        base_url: Optional[str] = None,
        timeout: Optional[Union[float, Dict[str, float]]] = None,
        retry: Optional[Dict[str, Any]] = None,
        debug: bool = False,
    ):
        """
        Initialize MotionOS client.

        Args:
            api_key: Your API key (sb_secret_xxx or sb_publishable_xxx)
            project_id: Your project ID
            base_url: Base URL for API (default: https://api.motionos.ai)
            timeout: Timeout in seconds. Can be a number or dict with 'ingest', 'retrieve', 'default'
            retry: Retry configuration dict with 'attempts' and 'backoff_ms'
            debug: Enable debug logging (default: False)

        Raises:
            InvalidAPIKeyError: If API key format is invalid
            InvalidRequestError: If project_id is empty
        """
        # Validate API key
        is_valid, key_type, error_msg = validate_api_key(api_key)
        if not is_valid:
            raise InvalidAPIKeyError(error_msg or "Invalid API key format")
        self.api_key = api_key.strip()
        self.key_type: ApiKeyType = key_type

        # Validate project ID
        if not project_id or not isinstance(project_id, str) or not project_id.strip():
            raise InvalidRequestError("Project ID is required and must be a non-empty string")
        self.project_id = project_id.strip()

        # Set base URL
        self.base_url = (base_url or "https://api.motionos.ai").rstrip("/")

        # Configure timeouts
        if isinstance(timeout, dict):
            self.timeout = TimeoutConfig(
                ingest=timeout.get("ingest", 12.0),
                retrieve=timeout.get("retrieve", 6.0),
                default=timeout.get("default", 10.0),
            )
        elif isinstance(timeout, (int, float)):
            self.timeout = TimeoutConfig(
                ingest=float(timeout),
                retrieve=float(timeout),
                default=float(timeout),
            )
        else:
            self.timeout = TimeoutConfig(ingest=12.0, retrieve=6.0, default=10.0)

        # Configure retries
        retry_attempts = (retry or {}).get("attempts", 2)
        retry_backoff = (retry or {}).get("backoff_ms", 300)
        self.retry_config = RetryConfig(attempts=retry_attempts, backoff_ms=retry_backoff)

        # Debug mode
        self.debug = debug
        if debug:
            logging.basicConfig(level=logging.DEBUG)

        # Default agent
        self.default_agent: Optional[str] = None

        # Create requests session with retry strategy
        self.session = requests.Session()
        retry_strategy = Retry(
            total=retry_attempts,
            backoff_factor=retry_backoff / 1000.0,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST"],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        logger.debug(
            "MotionOS client initialized",
            extra={
                "base_url": self.base_url,
                "project_id": self.project_id,
                "key_type": self.key_type,
                "timeout": self.timeout.__dict__,
                "sdk_version": SDK_VERSION,
            },
        )

    def _request(
        self,
        method: str,
        path: str,
        body: Optional[Dict[str, Any]] = None,
        operation: str = "other",
        retryable: bool = True,
    ) -> Dict[str, Any]:
        """
        Make HTTP request to MotionOS API.

        Args:
            method: HTTP method (GET, POST, etc.)
            path: API path (e.g., '/v1/memory/ingest')
            body: Request body (optional)
            operation: Operation type for timeout selection
            retryable: Whether request is retryable

        Returns:
            Response JSON as dict

        Raises:
            MotionOSError: On API error
        """
        # Validate operation
        is_allowed, error_msg = validate_operation(operation, self.key_type)
        if not is_allowed:
            raise ForbiddenError(error_msg or "Operation not allowed")

        request_id = generate_request_id()
        url = f"{self.base_url}{path}"
        timeout = (
            self.timeout.ingest
            if operation == "ingest"
            else (self.timeout.retrieve if operation == "retrieve" else self.timeout.default)
        )

        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key,
            "x-motionos-client-request-id": request_id,
            "x-motionos-sdk-version": SDK_VERSION,
        }

        last_error: Optional[Exception] = None

        for attempt in range(self.retry_config.attempts + 1):
            if attempt > 0 and retryable:
                delay = exponential_backoff(attempt, self.retry_config.backoff_ms)
                logger.debug(f"Retry attempt {attempt} after {delay}s")
                time.sleep(delay)

            try:
                if self.debug:
                    logger.debug(
                        f"{method} {path}",
                        extra={
                            "request_id": request_id,
                            "body": sanitize_for_logging(body or {}),
                        },
                    )

                response = self.session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=body,
                    timeout=timeout,
                )

                # Parse response
                try:
                    data = response.json()
                except (ValueError, json.JSONDecodeError):
                    raise create_motionos_error(
                        "Invalid JSON response from server",
                        "engine_unavailable",
                        response.status_code,
                    )

                # Handle errors
                if not response.ok:
                    error = create_motionos_error(data, "unknown_error", response.status_code)

                    # Handle rate limiting
                    if response.status_code == 429:
                        retry_after = response.headers.get("Retry-After")
                        if retry_after and attempt < self.retry_config.attempts:
                            time.sleep(int(retry_after))
                            continue

                    # Don't retry on client errors (4xx) except 429
                    if 400 <= response.status_code < 500 and response.status_code != 429:
                        raise error

                    # Retry server errors if retryable
                    if retryable and attempt < self.retry_config.attempts:
                        last_error = error
                        continue

                    raise error

                if self.debug:
                    logger.debug(
                        f"{method} {path} completed",
                        extra={
                            "request_id": request_id,
                            "status": response.status_code,
                        },
                    )

                return data

            except requests.exceptions.Timeout as e:
                raise create_motionos_error(
                    f"Request timeout after {timeout}s",
                    "timeout",
                    504,
                )
            except requests.exceptions.ConnectionError as e:
                if attempt < self.retry_config.attempts and retryable:
                    last_error = e
                    continue
                raise create_motionos_error("Network error - please check your connection", "network_error")
            except MotionOSError:
                raise
            except Exception as e:
                if attempt == self.retry_config.attempts or not retryable:
                    raise create_motionos_error(str(e), "unknown_error")
                last_error = e

        # If we exhausted retries
        if last_error:
            raise create_motionos_error("Request failed after retries", "network_error")

        raise create_motionos_error("Request failed", "unknown_error")

    def ingest(self, input: IngestInput) -> IngestResult:
        """
        Ingest memory into MotionOS.

        Args:
            input: String or IngestOptions dict

        Returns:
            IngestResult with id, summary, version_id

        Example:
            ```python
            # Simple string
            result = client.ingest("User prefers dark mode")

            # With options
            result = client.ingest({
                "raw_text": "User prefers dark mode",
                "agent_id": "assistant-1",
                "tags": ["preferences"]
            })
            ```
        """
        # Normalize input
        if isinstance(input, str):
            options: IngestOptions = {"raw_text": input}
        else:
            options = input

        # Validate
        if not options.get("raw_text") or not isinstance(options["raw_text"], str):
            raise InvalidRequestError("raw_text is required and must be a non-empty string")
        if not options["raw_text"].strip():
            raise InvalidRequestError("raw_text cannot be empty")

        # Validate scores
        if "importance" in options and options["importance"] is not None:
            if not 0 <= options["importance"] <= 1:
                raise InvalidRequestError("importance must be between 0 and 1")
        if "frequency" in options and options["frequency"] is not None:
            if options["frequency"] < 0:
                raise InvalidRequestError("frequency must be >= 0")
        if "recency" in options and options["recency"] is not None:
            if not 0 <= options["recency"] <= 1:
                raise InvalidRequestError("recency must be between 0 and 1")

        # Build payload
        payload: Dict[str, Any] = {
            "project_id": self.project_id,
            "raw_text": options["raw_text"].strip(),
            "agent_id": options.get("agent_id") or self.default_agent or "default-agent",
            "scope": options.get("scope") or "global",
        }

        # Add optional fields
        if "type" in options:
            payload["type"] = options["type"]
        if "tags" in options:
            payload["tags"] = options["tags"]
        if "summary" in options:
            payload["summary"] = options["summary"]
        if "source" in options:
            payload["source"] = options["source"]
        if "importance" in options:
            payload["importance"] = options["importance"]
        if "frequency" in options:
            payload["frequency"] = options["frequency"]
        if "recency" in options:
            payload["recency"] = options["recency"]

        # Handle event_time
        if "event_time" in options and options["event_time"]:
            event_time = options["event_time"]
            if isinstance(event_time, str):
                payload["event_time"] = event_time
            else:
                payload["event_time"] = event_time.isoformat()

        # Handle edges
        if "edges" in options and options["edges"]:
            payload["edges"] = [
                {"to": e["to"], "type": e.get("type", "causes")} for e in options["edges"]
            ]

        # Remove None values
        payload = remove_undefined(payload)

        try:
            response = self._request("POST", "/v1/memory/ingest", payload, "ingest", retryable=False)
            return IngestResult(
                id=response["id"],
                summary=response.get("summary", ""),
                version_id=response.get("version_id"),
                metadata={},
            )
        except MotionOSError:
            raise
        except Exception as e:
            raise create_motionos_error("Ingest failed", "engine_unavailable")

    def retrieve(self, input: RetrieveInput = "") -> RetrievalResult:
        """
        Retrieve memory from MotionOS.

        Args:
            input: Query string or RetrieveOptions dict (default: empty string)

        Returns:
            RetrievalResult with context, items, reasoning, meta

        Example:
            ```python
            # Simple query
            result = client.retrieve("user preferences")

            # With options
            result = client.retrieve({
                "query": "user preferences",
                "mode": "raw",
                "limit": 10
            })
            ```
        """
        # Normalize input
        if isinstance(input, str):
            options: RetrieveOptions = {"query": input}
        else:
            options = input

        # Validate limit
        limit = options.get("limit", 5)
        if not (1 <= limit <= 50):
            raise InvalidRequestError("limit must be between 1 and 50")

        # Build payload
        payload: Dict[str, Any] = {
            "project_id": self.project_id,
            "mode": options.get("mode", "inject"),
            "limit": limit,
        }

        if "query" in options:
            payload["query"] = options["query"]
        if "agent_id" in options:
            payload["agent_id"] = options["agent_id"]
        if "scope" in options:
            payload["scope"] = options["scope"]
        if "timeline_version_id" in options:
            payload["timeline_version_id"] = options["timeline_version_id"]

        # Build filters
        filters: Dict[str, Any] = {}
        if "tags" in options:
            filters["tags"] = options["tags"]
        if "types" in options:
            filters["types"] = options["types"]
        if "source" in options:
            filters["source"] = options["source"]
        if "after_time" in options:
            after_time = options["after_time"]
            filters["after_time"] = after_time.isoformat() if hasattr(after_time, "isoformat") else after_time
        if "before_time" in options:
            before_time = options["before_time"]
            filters["before_time"] = (
                before_time.isoformat() if hasattr(before_time, "isoformat") else before_time
            )
        if "latest_only" in options:
            filters["latest_only"] = options["latest_only"]

        if filters:
            payload["filters"] = filters

        payload = remove_undefined(payload)

        try:
            response = self._request("POST", "/v1/memory/retrieve", payload, "retrieve", retryable=True)

            # Normalize response
            items_data = response.get("items", []) or []
            items = [
                MemoryItem(
                    id=item["id"],
                    summary=item.get("summary") or "",
                    content=item.get("content", ""),
                    metadata=item.get("metadata", {}),
                    created_at=item.get("created_at", ""),
                    updated_at=item.get("updated_at", ""),
                    score=item.get("score", 0.0),
                )
                for item in items_data
            ]

            meta = response.get("meta", {})
            format_type = meta.get("format") or meta.get("mode") or options.get("mode", "inject")

            return RetrievalResult(
                context=response.get("context", ""),
                items=items,
                reasoning=response.get("reasoning", ""),
                meta={
                    "mode": "retrieval",
                    "format": format_type,
                    "limit": limit,
                    "query": options.get("query"),
                },
            )
        except MotionOSError:
            raise
        except Exception as e:
            raise create_motionos_error("Retrieve failed", "engine_unavailable")

    def rollback(self, options: RollbackOptions) -> RollbackResult:
        """
        Rollback memory to a previous version.

        Args:
            options: RollbackOptions with memory_id and version_id

        Returns:
            RollbackResult with ok boolean

        Example:
            ```python
            result = client.rollback(RollbackOptions(
                memory_id="mem-123",
                version_id="ver-456"
            ))
            ```
        """
        if not options.memory_id or not isinstance(options.memory_id, str):
            raise InvalidRequestError("memory_id is required and must be a string")
        if not options.version_id or not isinstance(options.version_id, str):
            raise InvalidRequestError("version_id is required and must be a string")

        payload = {"project_id": self.project_id, "version_id": options.version_id}

        try:
            response = self._request(
                "POST",
                f"/v1/memory/{options.memory_id}/rollback",
                payload,
                "rollback",
                retryable=False,
            )
            return RollbackResult(ok=response.get("ok", True))
        except MotionOSError:
            raise
        except Exception as e:
            raise create_motionos_error("Rollback failed", "engine_unavailable")

    def batch_ingest(self, options: BatchIngestOptions) -> BatchIngestResult:
        """
        Batch ingest multiple memories.

        Args:
            options: BatchIngestOptions with items list and optional chunk_size

        Returns:
            BatchIngestResult with results list

        Example:
            ```python
            result = client.batch_ingest(BatchIngestOptions(
                items=[
                    {"raw_text": "Memory 1"},
                    {"raw_text": "Memory 2"}
                ],
                chunk_size=10
            ))
            ```
        """
        if not options.items or not isinstance(options.items, list):
            raise InvalidRequestError("items is required and must be a non-empty list")

        chunk_size = options.chunk_size or 10
        chunks = chunk_list(options.items, chunk_size)
        results: List[BatchIngestResultItem] = []

        for chunk_items in chunks:
            for item in chunk_items:
                try:
                    ingest_result = self.ingest(item)
                    results.append(BatchIngestResultItem(id=ingest_result.id))
                except Exception as e:
                    error = e if isinstance(e, MotionOSError) else create_motionos_error(str(e), "unknown_error")
                    results.append(BatchIngestResultItem(error=error))

        return BatchIngestResult(results=results)

    def get_memory_by_id(self, memory_id: str) -> Optional[MemoryItem]:
        """
        Get a single memory by ID.

        Args:
            memory_id: Memory ID

        Returns:
            MemoryItem or None if not found
        """
        if not memory_id or not isinstance(memory_id, str):
            raise InvalidRequestError("Memory ID is required and must be a string")

        try:
            # Use retrieve to find by ID
            result = self.retrieve({"query": "", "mode": "raw", "limit": 100})
            for item in result.items:
                if item.id == memory_id:
                    return item
            return None
        except MotionOSError as e:
            if e.code == "not_found":
                return None
            raise

    def list_versions(self, memory_id: str) -> List[VersionInfo]:
        """
        List all versions for a memory.

        Args:
            memory_id: Memory ID

        Returns:
            List of VersionInfo
        """
        if not memory_id or not isinstance(memory_id, str):
            raise InvalidRequestError("Memory ID is required and must be a string")

        try:
            response = self._request("GET", f"/v1/memory/{memory_id}/versions", None, "other", retryable=True)
            versions_data = response.get("versions", [])
            return [
                VersionInfo(
                    id=v["id"],
                    memory_id=v["memory_id"],
                    version=v["version"],
                    content=v["content"],
                    summary=v["summary"],
                    created_at=v["created_at"],
                )
                for v in versions_data
            ]
        except MotionOSError as e:
            if e.code == "not_found":
                return []
            raise

    def health(self) -> Dict[str, str]:
        """
        Check API health status.

        Returns:
            Dict with status and service
        """
        return self._request("GET", "/health", None, "other", retryable=True)

    def get_config(self) -> SDKConfig:
        """Get current SDK configuration (for debugging)."""
        return SDKConfig(
            base_url=self.base_url,
            project_id=self.project_id,
            timeout=self.timeout,
            retry=self.retry_config,
            debug=self.debug,
            sdk_version=SDK_VERSION,
        )

    def set_default_agent(self, agent_id: str) -> "MotionOS":
        """
        Set default agent ID for ingest operations.

        Args:
            agent_id: Agent ID

        Returns:
            Self for chaining
        """
        self.default_agent = agent_id
        return self


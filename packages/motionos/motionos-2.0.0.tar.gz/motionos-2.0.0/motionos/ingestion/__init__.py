"""
MotionOS SDK - Ingestion Package

Memory ingestion with validation and builder pattern.
"""

from motionos.ingestion.builder import (
    IngestBuilder,
    ingest,
    ingest_decision,
    ingest_preference,
    ingest_fact,
)
from motionos.ingestion.validator import (
    validate_ingest_options,
    validate_raw_text,
    normalize_ingest_options,
    VALID_MEMORY_TYPES,
    VALID_SCOPES,
)

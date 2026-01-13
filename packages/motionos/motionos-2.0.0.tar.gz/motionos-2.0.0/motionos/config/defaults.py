"""
MotionOS SDK - Configuration Defaults

Default values for SDK configuration.
"""

# SDK Version - updated on each release
SDK_VERSION = "2.0.0"

# Base URL - HARDCODED per specification
# The SDK never allows this to be configured.
BASE_URL = "https://api.digicrest.site"

# Default timeout values (in seconds)
DEFAULT_INGEST_TIMEOUT = 12.0
DEFAULT_RETRIEVE_TIMEOUT = 6.0
DEFAULT_TIMEOUT = 10.0

# Default retry values
DEFAULT_RETRY_ATTEMPTS = 2
DEFAULT_BACKOFF_MS = 300
DEFAULT_MAX_BACKOFF_MS = 5000

# API key prefixes
API_KEY_PREFIX_SECRET = "sb_secret_"
API_KEY_PREFIX_PUBLISHABLE = "sb_publishable_"

# Minimum API key length
MIN_API_KEY_LENGTH = 20

# Default agent ID
DEFAULT_AGENT_ID = "default-agent"

# Default scope
DEFAULT_SCOPE = "global"

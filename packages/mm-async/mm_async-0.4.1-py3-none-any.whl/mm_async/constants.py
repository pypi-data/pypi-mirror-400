"""Default configuration constants for mm-async client."""


class RetryDefaults:
    """Default values for retry configuration."""

    MAX_ATTEMPTS: int = 3
    """Maximum number of retry attempts."""

    BASE_DELAY: float = 1.0
    """Base delay in seconds between retries."""

    MAX_DELAY: float = 30.0
    """Maximum delay in seconds between retries."""

    EXPONENTIAL_BASE: float = 2.0
    """Base for exponential backoff calculation."""

    JITTER_FACTOR: float = 0.1
    """Jitter factor as fraction of delay (0.1 = 10%)."""


class ClientDefaults:
    """Default values for client configuration."""

    TIMEOUT: float = 30.0
    """Default request timeout in seconds."""

    CONNECT_TIMEOUT: float = 10.0
    """Default connection timeout in seconds."""


class HttpStatus:
    """HTTP status codes used for error handling."""

    UNAUTHORIZED: int = 401
    FORBIDDEN: int = 403
    NOT_FOUND: int = 404
    RATE_LIMITED: int = 429
    SERVER_ERROR: int = 500


RETRYABLE_STATUS_CODES: frozenset[int] = frozenset({500, 502, 503, 504, 429})
"""HTTP status codes that trigger automatic retry."""

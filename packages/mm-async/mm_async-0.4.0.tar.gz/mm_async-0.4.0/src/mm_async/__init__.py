"""Async HTTP client for Mattermost API."""

from .client import AsyncMattermostClient
from .exceptions import (
    MattermostAuthError,
    MattermostConnectionError,
    MattermostError,
    MattermostForbiddenError,
    MattermostNotFoundError,
    MattermostRateLimitError,
    MattermostServerError,
    MattermostValidationError,
)
from .constants import ClientDefaults, HttpStatus, RetryDefaults
from .models import (
    Channel,
    ChannelMember,
    Post,
    Team,
    TeamMember,
    User,
)

__version__ = "0.4.0"

__all__ = [
    # Client
    "AsyncMattermostClient",
    # Exceptions
    "MattermostError",
    "MattermostAuthError",
    "MattermostForbiddenError",
    "MattermostNotFoundError",
    "MattermostRateLimitError",
    "MattermostServerError",
    "MattermostConnectionError",
    "MattermostValidationError",
    # Models
    "User",
    "Team",
    "Channel",
    "Post",
    "TeamMember",
    "ChannelMember",
    # Constants
    "ClientDefaults",
    "RetryDefaults",
    "HttpStatus",
]

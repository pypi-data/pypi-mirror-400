# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.4.0] - 2025-01-07

### Added

- `py.typed` marker for PEP 561 compliance (type checking support)
- CONTRIBUTING.md with development guidelines
- Comprehensive edge case test suite (16 new tests):
  - Network partition recovery tests (connection drop, retry, timeout)
  - Partial response handling tests (incomplete JSON, empty body, malformed errors)
  - Concurrent request handling tests (parallel requests, mixed operations, failure scenarios)
  - Malformed JSON handling tests (invalid syntax, unexpected types, null, unicode)
  - Connection pool exhaustion tests (sequential requests, context manager cleanup)
- Additional dev dependencies: mypy, pytest-cov, pre-commit
- `constants.py` module with `ClientDefaults`, `RetryDefaults`, `HttpStatus`
- `patch()` method for partial updates
- `post_file()` method for multipart file uploads

### Changed

- **Code style: Enforced strict PEP 8 line length (79 characters)** across entire codebase
- Replaced magic numbers with named constants in `client.py` and `retry.py`
- Unified exception messages format: "Connection error: ..." and "Request timeout: ..."
- Added pagination support (`page`, `per_page`) to search methods:
  - `users.search()`
  - `teams.search()`
  - `channels.search()`, `channels.get_by_team()`, `channels.get_my_channels_in_team()`
- Extended Pydantic models with additional API fields:
  - `User`: `auth_data`, `auth_service`, `mfa_active`, `props`, `notify_props`, timestamps, timezone
  - `Team`: `create_at`, `update_at`, `delete_at`, `scheme_id`, `email`, `allowed_domains`, `invite_id`, `allow_open_invite`
  - `Channel`: `create_at`, `update_at`, `delete_at`, `creator_id`, `total_msg_count`, `last_post_at`, `extra_update_at`, `scheme_id`
  - `Post`: `edit_at`, `delete_at`, `type`, `hashtags`, `file_ids`, `has_reactions`, `props`, `metadata`, `pending_post_id`
  - `TeamMember` and `ChannelMember`: `scheme_admin`, `scheme_user`

### Tests

- Total test count: 321 (305 unit tests + 16 edge case tests)
- All tests passing with 100% reliability

## [0.3.4] - 2025-01-07

### Added

- `channels.get_my_channels_in_team(team_id)` - Get all channels (public and private) that the current user is a member of in a specific team. Uses `/users/me/teams/{team_id}/channels` endpoint.

## [0.3.3] - 2024-12-26

### Added

- `channels.list_channels()` - List all channels with optional team filtering (requires `manage_system` permission)
- `channels.get_members()` - Get paginated list of channel members

### Fixed

- Synchronized version between `pyproject.toml` and `__init__.py`

## [0.3.2] - 2024-12-26

### Added

- `channels.search(team_id, term)` - Search for channels in a team by name
- `channels.get_by_name(team_id, name)` - Get channel by exact name
- `channels.create()` - Create new public or private channel
- `channels.delete()` - Delete a channel

## [0.3.1] - 2024-12-25

### Added

- `posts.search()` - Search posts with various filters
- `posts.get_thread()` - Get all posts in a thread

### Fixed

- Improved error messages for validation errors

## [0.3.0] - 2024-12-24

### Added

- High-Level API with namespaced methods (`client.users`, `client.teams`, `client.channels`, `client.posts`)
- Pydantic models for all API responses
- Automatic retry with exponential backoff for GET/DELETE requests
- Rate limit handling with `Retry-After` header support
- Comprehensive exception hierarchy

### Changed

- Complete rewrite from sync to async using httpx
- Token storage using `SecretStr` for security

## [0.2.0] - 2024-12-20

### Added

- Initial async client implementation
- Basic user and team operations

## [0.1.0] - 2024-12-15

### Added

- Project initialization
- Basic project structure

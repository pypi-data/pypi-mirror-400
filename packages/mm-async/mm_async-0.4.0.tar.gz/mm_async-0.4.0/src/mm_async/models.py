"""Pydantic models for Mattermost API responses."""

from typing import Any

from pydantic import BaseModel, ConfigDict


class User(BaseModel):
    """Mattermost user model."""

    model_config = ConfigDict(extra="ignore")

    id: str
    username: str
    email: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    nickname: str | None = None
    position: str | None = None
    roles: str | None = None
    # Extended fields
    auth_data: str | None = None
    auth_service: str | None = None
    mfa_active: bool | None = None
    props: dict[str, Any] | None = None
    notify_props: dict[str, Any] | None = None
    create_at: int | None = None
    update_at: int | None = None
    delete_at: int | None = None
    locale: str | None = None
    timezone: dict[str, Any] | None = None


class Team(BaseModel):
    """Mattermost team model."""

    model_config = ConfigDict(extra="ignore")

    id: str
    name: str
    display_name: str
    type: str  # "O" (open) | "I" (invite-only)
    description: str | None = None
    # Extended fields
    create_at: int | None = None
    update_at: int | None = None
    delete_at: int | None = None
    scheme_id: str | None = None
    email: str | None = None
    allowed_domains: str | None = None
    invite_id: str | None = None
    allow_open_invite: bool | None = None


class Channel(BaseModel):
    """Mattermost channel model."""

    model_config = ConfigDict(extra="ignore")

    id: str
    team_id: str
    name: str
    display_name: str
    type: str  # "O" (public) | "P" (private) | "D" (direct) | "G" (group)
    header: str | None = None
    purpose: str | None = None
    # Extended fields
    create_at: int | None = None
    update_at: int | None = None
    delete_at: int | None = None
    creator_id: str | None = None
    total_msg_count: int | None = None
    last_post_at: int | None = None
    extra_update_at: int | None = None
    scheme_id: str | None = None


class Post(BaseModel):
    """Mattermost post model."""

    model_config = ConfigDict(extra="ignore")

    id: str
    channel_id: str
    user_id: str
    message: str
    root_id: str | None = None
    create_at: int | None = None
    update_at: int | None = None
    # Extended fields
    edit_at: int | None = None
    delete_at: int | None = None
    type: str | None = None
    hashtags: str | None = None
    file_ids: list[str] | None = None
    has_reactions: bool | None = None
    props: dict[str, Any] | None = None
    metadata: dict[str, Any] | None = None
    pending_post_id: str | None = None


class TeamMember(BaseModel):
    """Mattermost team member model."""

    model_config = ConfigDict(extra="ignore")

    team_id: str
    user_id: str
    roles: str
    delete_at: int | None = None
    scheme_admin: bool | None = None
    scheme_user: bool | None = None


class ChannelMember(BaseModel):
    """Mattermost channel member model."""

    model_config = ConfigDict(extra="ignore")

    channel_id: str
    user_id: str
    roles: str
    scheme_admin: bool | None = None
    scheme_user: bool | None = None

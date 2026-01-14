"""Pydantic models for configuration."""

import os
from datetime import datetime
from typing import Dict, Optional
from pydantic import BaseModel, Field


class AuthConfig(BaseModel):
    """Authentication configuration."""

    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    expires_at: Optional[datetime] = None
    user_id: Optional[str] = None
    user_email: Optional[str] = None


class OrganizationInfo(BaseModel):
    """Organization information."""

    id: str
    name: str
    uuid: str


class APIConfig(BaseModel):
    """API configuration."""

    # Production URL by default, override with env var for development
    base_url: str = Field(
        default_factory=lambda: os.getenv(
            "JANET_API_BASE_URL",
            "https://janet-ai-backend-prod-service-11399-85b8d46f-d4i7j6xw.onporter.run"
        )
    )
    timeout: int = 30


class SyncConfig(BaseModel):
    """Sync configuration."""

    root_directory: str = "~/janet-tickets"
    last_sync_times: Dict[str, str] = Field(default_factory=dict)
    sync_on_init: bool = False
    batch_size: int = 50


class MarkdownConfig(BaseModel):
    """Markdown generation configuration."""

    include_comments: bool = True
    include_attachments: bool = True
    include_metadata: bool = True
    yjs_fallback_mode: str = "plain_text"


class Config(BaseModel):
    """Complete configuration model."""

    version: str = "1.0"
    auth: AuthConfig = Field(default_factory=AuthConfig)
    selected_organization: Optional[OrganizationInfo] = None
    api: APIConfig = Field(default_factory=APIConfig)
    sync: SyncConfig = Field(default_factory=SyncConfig)
    markdown: MarkdownConfig = Field(default_factory=MarkdownConfig)

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from pydantic import BaseModel, ConfigDict, Field

if TYPE_CHECKING:
    from .oauth_client import OAuthClient


class OAuthToken(BaseModel):
    """OAuth token represents a VCS configuration including the associated OAuth token."""

    model_config = ConfigDict(extra="forbid")

    id: str = Field(..., description="OAuth token ID")
    uid: str = Field(..., description="OAuth token UID")
    created_at: datetime = Field(..., description="Creation timestamp")
    has_ssh_key: bool = Field(..., description="Whether the token has an SSH key")
    service_provider_user: str = Field(..., description="Service provider user")

    # Relationships
    oauth_client: OAuthClient | None = Field(
        None, description="The associated OAuth client"
    )


class OAuthTokenList(BaseModel):
    """List of OAuth tokens with pagination information."""

    model_config = ConfigDict(extra="forbid")

    items: list[OAuthToken] = Field(default_factory=list, description="OAuth tokens")
    current_page: int | None = Field(None, description="Current page number")
    prev_page: int | None = Field(None, description="Previous page number")
    next_page: int | None = Field(None, description="Next page number")
    total_pages: int | None = Field(None, description="Total number of pages")
    total_count: int | None = Field(None, description="Total count of items")


class OAuthTokenListOptions(BaseModel):
    """Options for listing OAuth tokens."""

    model_config = ConfigDict(extra="forbid")

    page_number: int | None = Field(None, description="Page number")
    page_size: int | None = Field(None, description="Page size")


class OAuthTokenUpdateOptions(BaseModel):
    """Options for updating an OAuth token."""

    model_config = ConfigDict(extra="forbid")

    private_ssh_key: str | None = Field(
        None, description="A private SSH key to be used for git clone operations"
    )


# Rebuild models to resolve forward references
try:
    from .oauth_client import OAuthClient  # noqa: F401

    OAuthToken.model_rebuild()
    OAuthTokenList.model_rebuild()
except ImportError:
    # If OAuthClient is not available, create a dummy class
    pass

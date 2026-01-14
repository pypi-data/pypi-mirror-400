from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ReservedTagKey(BaseModel):
    """Represents a reserved tag key in Terraform Enterprise."""

    model_config = ConfigDict(populate_by_name=True)

    id: str = Field(..., description="The unique identifier for this reserved tag key")
    type: str = Field(
        default="reserved-tag-keys", description="The type of this resource"
    )
    key: str = Field(..., description="The key targeted by this reserved tag key")
    disable_overrides: bool = Field(
        ...,
        alias="disable-overrides",
        description="If true, disables overriding inherited tags with the specified key at the workspace level",
    )
    created_at: datetime | None = Field(
        None,
        alias="created-at",
        description="The time when the reserved tag key was created",
    )
    updated_at: datetime | None = Field(
        None,
        alias="updated-at",
        description="The time when the reserved tag key was last updated",
    )


class ReservedTagKeyCreateOptions(BaseModel):
    """Options for creating a new reserved tag key."""

    model_config = ConfigDict(populate_by_name=True)

    key: str = Field(..., description="The key targeted by this reserved tag key")
    disable_overrides: bool = Field(
        ...,
        alias="disable-overrides",
        description="If true, disables overriding inherited tags with the specified key at the workspace level",
    )


class ReservedTagKeyUpdateOptions(BaseModel):
    """Options for updating a reserved tag key."""

    model_config = ConfigDict(populate_by_name=True)

    key: str | None = Field(
        None, description="The key targeted by this reserved tag key"
    )
    disable_overrides: bool | None = Field(
        None,
        alias="disable-overrides",
        description="If true, disables overriding inherited tags with the specified key at the workspace level",
    )


class ReservedTagKeyListOptions(BaseModel):
    """Options for listing reserved tag keys."""

    model_config = ConfigDict(populate_by_name=True)

    page_number: int | None = Field(
        None, alias="page[number]", description="Page number to retrieve", ge=1
    )
    page_size: int | None = Field(
        None, alias="page[size]", description="Number of items per page", ge=1, le=100
    )


class ReservedTagKeyList(BaseModel):
    """Represents a paginated list of reserved tag keys."""

    model_config = ConfigDict(populate_by_name=True)

    items: list[ReservedTagKey] = Field(
        default_factory=list, description="List of reserved tag keys"
    )
    current_page: int | None = Field(None, description="Current page number")
    total_pages: int | None = Field(None, description="Total number of pages")
    prev_page: str | None = Field(None, description="URL of the previous page")
    next_page: str | None = Field(None, description="URL of the next page")
    total_count: int | None = Field(None, description="Total number of items")

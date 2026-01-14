from __future__ import annotations

from typing import Any

from ..errors import (
    InvalidOrgError,
    ValidationError,
)
from ..models.reserved_tag_key import (
    ReservedTagKey as ReservedTagKeyModel,
)
from ..models.reserved_tag_key import (
    ReservedTagKeyCreateOptions,
    ReservedTagKeyList,
    ReservedTagKeyListOptions,
    ReservedTagKeyUpdateOptions,
)
from ..utils import valid_string_id
from ._base import _Service


class ReservedTagKey(_Service):
    """Reserved Tag Key API for Terraform Enterprise."""

    def list(
        self, organization: str, options: ReservedTagKeyListOptions | None = None
    ) -> ReservedTagKeyList:
        """List reserved tag keys for the given organization."""
        if not valid_string_id(organization):
            raise InvalidOrgError()

        params = (
            options.model_dump(by_alias=True, exclude_none=True) if options else None
        )

        r = self.t.request(
            "GET",
            f"/api/v2/organizations/{organization}/reserved-tag-keys",
            params=params,
        )

        jd = r.json()
        items = []
        meta = jd.get("meta", {})
        pagination = meta.get("pagination", {})

        for d in jd.get("data", []):
            items.append(self._parse_reserved_tag_key(d))

        return ReservedTagKeyList(
            items=items,
            current_page=pagination.get("current-page"),
            total_pages=pagination.get("total-pages"),
            prev_page=pagination.get("prev-page"),
            next_page=pagination.get("next-page"),
            total_count=pagination.get("total-count"),
        )

    def create(
        self, organization: str, options: ReservedTagKeyCreateOptions
    ) -> ReservedTagKeyModel:
        """Create a new reserved tag key for the given organization."""
        if not valid_string_id(organization):
            raise InvalidOrgError()

        attrs = options.model_dump(by_alias=True, exclude_none=True)
        body: dict[str, Any] = {
            "data": {
                "attributes": attrs,
                "type": "reserved-tag-keys",
            }
        }

        r = self.t.request(
            "POST",
            f"/api/v2/organizations/{organization}/reserved-tag-keys",
            json_body=body,
        )

        jd = r.json()
        data = jd.get("data", {})

        return self._parse_reserved_tag_key(data)

    def read(self, reserved_tag_key_id: str) -> ReservedTagKeyModel:
        """Read a reserved tag key by its ID."""
        if not valid_string_id(reserved_tag_key_id):
            raise ValidationError("Invalid reserved tag key ID")

        # Note: Based on the API docs, there's no explicit GET endpoint for individual reserved tag keys
        # This method would need to be implemented if such an endpoint exists
        raise NotImplementedError(
            "Individual reserved tag key read is not supported by the API"
        )

    def update(
        self, reserved_tag_key_id: str, options: ReservedTagKeyUpdateOptions
    ) -> ReservedTagKeyModel:
        """Update a reserved tag key."""
        if not valid_string_id(reserved_tag_key_id):
            raise ValidationError("Invalid reserved tag key ID")

        attrs = options.model_dump(by_alias=True, exclude_none=True)
        body: dict[str, Any] = {
            "data": {
                "attributes": attrs,
                "type": "reserved-tag-keys",
            }
        }

        r = self.t.request(
            "PATCH",
            f"/api/v2/reserved-tag-keys/{reserved_tag_key_id}",
            json_body=body,
        )

        jd = r.json()
        data = jd.get("data", {})

        return self._parse_reserved_tag_key(data)

    def delete(self, reserved_tag_key_id: str) -> None:
        """Delete a reserved tag key."""
        if not valid_string_id(reserved_tag_key_id):
            raise ValidationError("Invalid reserved tag key ID")

        self.t.request("DELETE", f"/api/v2/reserved-tag-keys/{reserved_tag_key_id}")
        # DELETE returns 204 No Content on success

    def _parse_reserved_tag_key(self, data: dict[str, Any]) -> ReservedTagKeyModel:
        """Parse reserved tag key data from API response."""
        attrs = data.get("attributes", {})
        attrs["id"] = data.get("id")
        return ReservedTagKeyModel.model_validate(attrs)

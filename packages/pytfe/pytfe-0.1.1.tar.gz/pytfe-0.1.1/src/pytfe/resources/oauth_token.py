from __future__ import annotations

from datetime import datetime
from typing import Any
from urllib.parse import quote

from ..errors import ERR_INVALID_OAUTH_TOKEN_ID, ERR_INVALID_ORG
from ..models.oauth_token import (
    OAuthToken,
    OAuthTokenList,
    OAuthTokenListOptions,
    OAuthTokenUpdateOptions,
)
from ..utils import encode_query, valid_string_id
from ._base import _Service


class OAuthTokens(_Service):
    """OAuth tokens service for managing VCS OAuth tokens."""

    def list(
        self, organization: str, options: OAuthTokenListOptions | None = None
    ) -> OAuthTokenList:
        """List all the OAuth tokens for a given organization."""
        if not valid_string_id(organization):
            raise ValueError(ERR_INVALID_ORG)

        path = f"/api/v2/organizations/{quote(organization)}/oauth-tokens"
        params = {}

        if options:
            if options.page_number:
                params["page[number]"] = str(options.page_number)
            if options.page_size:
                params["page[size]"] = str(options.page_size)

        query_string = encode_query(params)
        full_path = f"{path}{query_string}"

        response = self.t.request("GET", full_path)
        data = response.json()

        tokens = []
        if "data" in data:
            for item in data["data"]:
                tokens.append(self._parse_oauth_token(item))

        # Parse pagination metadata
        pagination = {}
        if "meta" in data:
            meta = data["meta"]
            if "pagination" in meta:
                page_info = meta["pagination"]
                pagination = {
                    "current_page": page_info.get("current-page"),
                    "prev_page": page_info.get("prev-page"),
                    "next_page": page_info.get("next-page"),
                    "total_pages": page_info.get("total-pages"),
                    "total_count": page_info.get("total-count"),
                }

        return OAuthTokenList(items=tokens, **pagination)

    def read(self, oauth_token_id: str) -> OAuthToken:
        """Read an OAuth token by its ID."""
        if not valid_string_id(oauth_token_id):
            raise ValueError(ERR_INVALID_OAUTH_TOKEN_ID)

        path = f"/api/v2/oauth-tokens/{quote(oauth_token_id)}"
        response = self.t.request("GET", path)
        data = response.json()

        if "data" in data:
            return self._parse_oauth_token(data["data"])

        raise ValueError("Invalid response format")

    def update(
        self, oauth_token_id: str, options: OAuthTokenUpdateOptions
    ) -> OAuthToken:
        """Update an existing OAuth token."""
        if not valid_string_id(oauth_token_id):
            raise ValueError(ERR_INVALID_OAUTH_TOKEN_ID)

        body: dict[str, Any] = {
            "data": {
                "type": "oauth-tokens",
                "attributes": {},
            }
        }

        if options.private_ssh_key is not None:
            body["data"]["attributes"]["ssh-key"] = options.private_ssh_key

        path = f"/api/v2/oauth-tokens/{quote(oauth_token_id)}"
        response = self.t.request("PATCH", path, json_body=body)
        data = response.json()

        if "data" in data:
            return self._parse_oauth_token(data["data"])

        raise ValueError("Invalid response format")

    def delete(self, oauth_token_id: str) -> None:
        """Delete an OAuth token by its ID."""
        if not valid_string_id(oauth_token_id):
            raise ValueError(ERR_INVALID_OAUTH_TOKEN_ID)

        path = f"/api/v2/oauth-tokens/{quote(oauth_token_id)}"
        self.t.request("DELETE", path)

    def _parse_oauth_token(self, data: dict[str, Any]) -> OAuthToken:
        """Parse OAuth token data from API response."""
        attributes = data.get("attributes", {})

        # Parse creation timestamp
        created_at_str = attributes.get("created-at")
        created_at = (
            datetime.fromisoformat(created_at_str.replace("Z", "+00:00"))
            if created_at_str
            else datetime.now()
        )

        # Parse OAuth client relationship
        oauth_client = None
        # For now, just set to None since it's mainly for display
        # The actual relationship data would require more complex parsing

        return OAuthToken(
            id=data.get("id", ""),
            uid=attributes.get("uid", ""),
            created_at=created_at,
            has_ssh_key=attributes.get("has-ssh-key", False),
            service_provider_user=attributes.get("service-provider-user", ""),
            oauth_client=oauth_client,
        )

"""Module for handling machine authentication and token management."""

import os
from datetime import datetime, timedelta
from typing import Any

import httpx


class IdentityService:
    """Service for handling machine authentication and token management."""

    def __init__(self):
        """Initialize the IdentityService with environment variables."""
        self.client_id = os.getenv("MACHINE_CLIENT_ID")
        self.client_secret = os.getenv("MACHINE_CLIENT_SECRET")
        self.base_url = os.getenv("UIPATH_URL")
        self.organization_id = os.getenv("UIPATH_ORGANIZATION_ID")
        self.tenant_id = os.getenv("UIPATH_TENANT_ID")

        if not all(
            [
                self.client_id,
                self.client_secret,
                self.base_url,
                self.organization_id,
                self.tenant_id,
            ]
        ):
            raise ValueError(
                "Missing required environment variables: MACHINE_CLIENT_ID, MACHINE_CLIENT_SECRET, UIPATH_URL, UIPATH_ORGANIZATION_ID, UIPATH_TENANT_ID"
            )

        self.access_token: str | None = None
        self.token_expiry: datetime | None = None

    async def get_token(self) -> str:
        """Get Service-to-Service access token using client credentials."""
        assert self.base_url is not None

        token_endpoint = f"{self.base_url.rstrip('/')}/identity_/connect/token"

        data = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "scope": "OrchestratorApiUserAccess",
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                token_endpoint,
                data=data,
            )
            response.raise_for_status()

            token_data: dict[str, Any] = response.json()
            self.access_token = token_data["access_token"]

            expires_in = token_data.get("expires_in", 3600)
            self.token_expiry = datetime.now() + timedelta(seconds=expires_in - 60)

            os.environ["MACHINE_ACCESS_TOKEN"] = self.access_token

            print(f"[{datetime.now()}] Token acquired successfully")
            return self.access_token

    def is_token_expired(self) -> bool:
        """Check if the current token is expired or about to expire."""
        if not self.access_token or not self.token_expiry:
            return True
        return datetime.now() >= self.token_expiry

    async def ensure_valid_token(self) -> str:
        """Ensure we have a valid token, refresh if needed."""
        if self.is_token_expired():
            await self.get_token()
        assert self.access_token is not None
        return self.access_token

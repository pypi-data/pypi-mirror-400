"""Orchestrator service to interact with UiPath Orchestrator APIs."""

import base64
import os
import platform
from pathlib import Path
from typing import Any

import httpx

from uipath.robot.infra import get_logger
from uipath.robot.models import HeartbeatData, HeartbeatResponse


class OrchestratorService:
    """Service for interacting with UiPath Orchestrator APIs."""

    def __init__(self):
        """Initialize the OrchestratorService with environment variables."""
        self.logger = get_logger()

        self.access_token = os.getenv("UIPATH_ACCESS_TOKEN")
        self.base_url = os.getenv("UIPATH_URL")

        if not self.access_token:
            raise ValueError("Missing UIPATH_ACCESS_TOKEN environment variable")
        if not self.base_url:
            raise ValueError("Missing UIPATH_URL environment variable")

    async def get_shared_connection_data(self) -> str | None:
        """Get shared connection data from Orchestrator.

        Returns:
            License key string if successful, None otherwise
        """
        assert self.base_url is not None

        url = f"{self.base_url.rstrip('/')}/orchestrator_/api/robotsservice/getsharedconnectiondata"

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, headers=headers)
                response.raise_for_status()

                data: dict[str, Any] = response.json()
                license_key = data.get("licenseKey")

                if license_key:
                    return license_key
                else:
                    self.logger.error("No LicenseKey found in response")
                    return None

            except httpx.HTTPStatusError as e:
                if e.response.status_code == 401:
                    self.logger.error("Unauthorized: Invalid or expired token")
                elif e.response.status_code == 409:
                    self.logger.error(f"Conflict error occurred: {e.response.text}")
                else:
                    self.logger.error(f"HTTP error: {e.response.status_code} - {e}")
                return None
            except httpx.HTTPError as e:
                self.logger.error(f"Request failed: {e}")
                return None
            except Exception as e:
                self.logger.error(f"Unexpected error: {e}")
                return None

    async def download_package(
        self,
        package_id: str,
        package_version: str,
        output_path: Path,
        feed_id: str | None = None,
    ) -> bool:
        """Download a package from Orchestrator.

        Args:
            package_id: The package identifier
            package_version: The package version
            output_path: Path where to save the downloaded package

        Returns:
            True if successful, False otherwise
        """
        assert self.base_url is not None

        url = f"{self.base_url.rstrip('/')}/orchestrator_/odata/Processes/UiPath.Server.Configuration.OData.DownloadPackage(key='{package_id}:{package_version}')"

        params = {}

        if feed_id:
            params["feedId"] = feed_id

        headers = {
            "Authorization": f"Bearer {self.access_token}",
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, params=params, headers=headers)
                response.raise_for_status()

                # Write the package content to file
                output_path.parent.mkdir(parents=True, exist_ok=True)
                with open(output_path, "wb") as f:
                    f.write(response.content)

                return True

            except httpx.HTTPStatusError as e:
                self.logger.error(
                    f"Failed to download package - HTTP {e.response.status_code}: {e}"
                )
                return False
            except httpx.HTTPError as e:
                self.logger.error(f"Failed to download package - Request error: {e}")
                return False
            except Exception as e:
                self.logger.error(f"Failed to download package - Unexpected error: {e}")
                return False

    async def heartbeat(self, license_key: str) -> HeartbeatResponse:
        """Send heartbeat to Orchestrator.

        Args:
            license_key: The robot license key. If None, uses stored license_key.

        Returns:
            HeartbeatResponse object containing commands from Orchestrator
        """
        assert self.base_url is not None

        url = f"{self.base_url.rstrip('/')}/orchestrator_/api/robotsservice/heartbeatv2"

        headers = {
            **self._get_robot_headers(license_key),
        }

        payload = {"CommandState": "All", "Heartbeats": []}

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, headers=headers, json=payload)
                response.raise_for_status()
                data = response.json()
                return HeartbeatResponse.model_validate(data)

            except httpx.HTTPStatusError as e:
                self.logger.error(
                    f"Heartbeat failed - HTTP {e.response.status_code}: {e}"
                )
                raise e
            except httpx.HTTPError as e:
                self.logger.error(f"Heartbeat failed - Request error: {e}")
                raise e
            except Exception as e:
                self.logger.error(f"Heartbeat failed - Unexpected error: {e}")
                raise e

    async def start_service(self, license_key: str) -> bool:
        """Send start service request to Orchestrator.

        Args:
            license_key: The robot license key.

        Returns:
            True if successful, False otherwise
        """
        assert self.base_url is not None

        url = (
            f"{self.base_url.rstrip('/')}/orchestrator_/api/robotsservice/startservice"
        )

        headers = {
            **self._get_robot_headers(license_key),
        }

        payload: dict[str, Any] = {}

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, headers=headers, json=payload)
                response.raise_for_status()
                return True

            except httpx.HTTPStatusError as e:
                self.logger.error(
                    f"Start service failed - HTTP {e.response.status_code}: {e}"
                )
                return False
            except httpx.HTTPError as e:
                self.logger.error(f"Start service failed - Request error: {e}")
                return False
            except Exception as e:
                self.logger.error(f"Start service failed - Unexpected error: {e}")
                return False

    async def stop_service(self, license_key: str) -> bool:
        """Send stop service request to Orchestrator.

        Args:
            license_key: The robot license key.

        Returns:
            True if successful, False otherwise
        """
        assert self.base_url is not None

        url = f"{self.base_url.rstrip('/')}/orchestrator_/api/robotsservice/stopservice"

        headers = {
            **self._get_robot_headers(license_key),
        }

        payload: dict[str, Any] = {}

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, headers=headers, json=payload)
                response.raise_for_status()
                return True

            except httpx.HTTPStatusError as e:
                self.logger.error(
                    f"Stop service failed - HTTP {e.response.status_code}: {e}"
                )
                return False
            except httpx.HTTPError as e:
                self.logger.error(f"Stop service failed - Request error: {e}")
                return False
            except Exception as e:
                self.logger.error(f"Stop service failed - Unexpected error: {e}")
                return False

    async def submit_job_state(
        self, heartbeats: list[HeartbeatData], license_key: str
    ) -> bool:
        """Submit job states to Orchestrator.

        Args:
            heartbeats: List of heartbeat data containing job states
            license_key: The robot license key

        Returns:
            True if successful, False otherwise
        """
        assert self.base_url is not None

        url = f"{self.base_url.rstrip('/')}/orchestrator_/api/robotsservice/SubmitJobState"

        headers = {
            **self._get_robot_headers(license_key),
        }

        payload = [heartbeat.model_dump(by_alias=True) for heartbeat in heartbeats]

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, headers=headers, json=payload)
                response.raise_for_status()
                return True

            except httpx.HTTPStatusError as e:
                self.logger.error(
                    f"Submit job state failed - HTTP {e.response.status_code}: {e}"
                )
                self.logger.error(f"Response: {e.response.text}")
                return False
            except httpx.HTTPError as e:
                self.logger.error(f"Submit job state failed - Request error: {e}")
                return False
            except Exception as e:
                self.logger.error(f"Submit job state failed - Unexpected error: {e}")
                return False

    def _get_robot_headers(self, license_key: str) -> dict[str, str]:
        """Get robot-specific headers for heartbeat calls.

        Args:
            license_key: The robot license key

        Returns:
            Dictionary of robot headers
        """
        machine = platform.node()
        hostname = f"{machine}-py"

        return {
            "X-ROBOT-VERSION": "24.10",
            "X-ROBOT-MACHINE": hostname,
            "X-ROBOT-MACHINE-ENCODED": base64.b64encode(
                hostname.encode("utf-8")
            ).decode("utf-8"),
            "X-ROBOT-LICENSE": license_key,
            "X-ROBOT-AGENT": "OS=Windows",
        }

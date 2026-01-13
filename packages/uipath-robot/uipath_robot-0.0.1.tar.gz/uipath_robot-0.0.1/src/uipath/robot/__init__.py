"""UiPath Robot Package Initialization."""

import asyncio
import json
import os
import subprocess
import uuid
import zipfile
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

from uipath.robot.infra import get_logger, init_logger
from uipath.robot.models import (
    Command,
    HeartbeatData,
    HeartbeatResponse,
    JobError,
    JobState,
    SessionState,
)
from uipath.robot.services import OrchestratorService


class Robot:
    """Main Robot class to manage interactions with UiPath Orchestrator."""

    def __init__(self, verbose: bool = False):
        """Initialize the Robot with necessary services.

        Args:
            verbose: Enable verbose logging
        """
        self.logger = get_logger(verbose)
        self.orchestrator = OrchestratorService()
        self.heartbeat_interval = 10  # seconds
        self.license_key: str | None = None

        base_dir = Path.cwd() / ".uipath"
        self.packages_dir = base_dir / "packages"
        self.processes_dir = base_dir / "processes"

        self.packages_dir.mkdir(parents=True, exist_ok=True)
        self.processes_dir.mkdir(parents=True, exist_ok=True)

    async def initialize(self) -> bool:
        """Initialize the service by getting connection data and license key.

        Returns:
            True if initialization successful, False otherwise
        """
        self.logger.info("Initializing robot service")

        self.license_key = await self.orchestrator.get_shared_connection_data()

        if not self.license_key:
            self.logger.error("Failed to get connection data")
            return False

        self.logger.success(f"Connected (key: {self.license_key[:10]}...)")
        return True

    def get_package_path(self, package_id: str, package_version: str) -> Path:
        """Get the path for a package zip file."""
        return self.packages_dir / f"{package_id}_{package_version}.zip"

    def get_process_path(self, package_id: str, package_version: str) -> Path:
        """Get the path for an extracted process."""
        return self.processes_dir / f"{package_id}_{package_version}"

    async def download_and_setup_package(
        self, package_id: str, package_version: str, feed_id: str | None = None
    ) -> Path | None:
        """Download package if needed, extract it, and setup environment.

        Args:
            package_id: The package identifier
            package_version: The package version
            feed_id: Optional feed identifier

        Returns:
            Path to the extracted process directory, or None if failed
        """
        package_path = self.get_package_path(package_id, package_version)
        process_path = self.get_process_path(package_id, package_version)

        # Check if already downloaded and extracted
        if process_path.exists():
            self.logger.package_status(package_id, package_version, "cached")
            return process_path

        # Download package if not exists
        if not package_path.exists():
            self.logger.package_status(package_id, package_version, "downloading")
            success = await self.orchestrator.download_package(
                package_id,
                package_version,
                package_path,
                feed_id,
            )
            if not success:
                self.logger.error("Failed to download package")
                return None
            self.logger.debug(f"Downloaded to {package_path}", indent=1)

        # Extract package - extract only the 'content' folder
        self.logger.package_status(package_id, package_version, "extracting")
        try:
            process_path.mkdir(parents=True, exist_ok=True)

            with zipfile.ZipFile(package_path, "r") as zip_ref:
                # Get all files in the 'content' folder
                content_files = [
                    f for f in zip_ref.namelist() if f.startswith("content/")
                ]

                if not content_files:
                    self.logger.error("No 'content' folder found in package")
                    return None

                # Extract each file, removing the 'content/' prefix
                for file in content_files:
                    if file == "content/":
                        continue

                    # Remove 'content/' prefix from the path
                    target_path = file[len("content/") :]

                    # Extract to process_path with adjusted path
                    if target_path:
                        source = zip_ref.open(file)
                        target = process_path / target_path
                        target.parent.mkdir(parents=True, exist_ok=True)

                        with source, open(target, "wb") as target_file:
                            target_file.write(source.read())

            self.logger.package_status(package_id, package_version, "extracted")
        except Exception as e:
            self.logger.error(f"Failed to extract: {e}")
            return None

        # Setup virtual environment only if pyproject.toml exists
        pyproject_path = process_path / "pyproject.toml"
        if pyproject_path.exists():
            self.logger.environment_setup("creating")
            venv_path = process_path / ".venv"
            try:
                subprocess.run(
                    ["uv", "venv", str(venv_path)],
                    cwd=process_path,
                    check=True,
                    capture_output=True,
                )

                env_with_temp = {"VIRTUAL_ENV": str(venv_path)}
                env_with_temp["TMPDIR"] = str(process_path / "temp")  # Linux/Mac
                env_with_temp["TEMP"] = str(process_path / "temp")  # Windows
                env_with_temp["TMP"] = str(process_path / "temp")  # Windows

                (process_path / "temp").mkdir(exist_ok=True)

                self.logger.environment_setup("syncing")
                subprocess.run(
                    ["uv", "sync"],
                    cwd=process_path,
                    env=env_with_temp,
                    check=True,
                    capture_output=True,
                    text=True,
                )
                self.logger.environment_setup("ready")

            except subprocess.CalledProcessError as e:
                self.logger.error(f"Environment setup failed: {e}")
                self.logger.debug(f"stdout: {e.stdout}", indent=1)
                self.logger.debug(f"stderr: {e.stderr}", indent=1)
                return None
            except Exception as e:
                self.logger.error(f"Unexpected error: {e}")
                return None
        else:
            self.logger.environment_setup("skipped")

        return process_path

    async def execute_process(self, process_path: Path, command: Command) -> None:
        """Execute a process using uipath run.

        Args:
            process_path: Path to the process directory
            command: The command data containing job details
        """
        assert self.license_key is not None
        self.logger.process_execution("starting")
        try:
            # Prepare environment variables
            env = os.environ.copy()
            env["UIPATH_JOB_KEY"] = command.data.job_key
            env["UIPATH_FOLDER_KEY"] = command.data.folder_key
            env["UIPATH_FOLDER_PATH"] = command.data.fully_qualified_folder_name
            env["UIPATH_PROCESS_UUID"] = command.data.process_key
            env["VIRTUAL_ENV"] = str(process_path / ".venv")

            trace_id = command.data.trace_id or str(uuid.uuid4())
            env["UIPATH_TRACE_ID"] = trace_id
            if command.data.parent_span_id:
                env["UIPATH_PARENT_SPAN_ID"] = command.data.parent_span_id
            if command.data.root_span_id:
                env["UIPATH_ROOT_SPAN_ID"] = command.data.root_span_id

            # Ensure required env vars are present
            required_vars = [
                "UIPATH_ACCESS_TOKEN",
                "UIPATH_URL",
                "UIPATH_TENANT_ID",
                "UIPATH_ORGANIZATION_ID",
            ]

            missing_vars = [var for var in required_vars if not env.get(var)]
            if missing_vars:
                self.logger.error(f"Missing env vars: {', '.join(missing_vars)}")
                return

            await self.orchestrator.submit_job_state(
                heartbeats=[
                    HeartbeatData(
                        robot_key=command.robot_key,
                        robot_state=SessionState.BUSY,
                        process_key=command.data.process_key,
                        job_key=command.data.job_key,
                        job_state=JobState.RUNNING,
                        trace_id=trace_id,
                    )
                ],
                license_key=self.license_key,
            )

            self.logger.process_execution("running")

            cmd = ["uv", "run", "uipath", "run"]
            if command.data.entry_point_path:
                cmd.extend([command.data.entry_point_path])
            if command.data.input_arguments:
                cmd.extend([command.data.input_arguments])

            result = subprocess.run(
                cmd,
                cwd=process_path,
                env=env,
                check=True,
                capture_output=True,
                text=True,
            )

            output_file = process_path / "__uipath" / "output.json"
            if output_file.exists():
                output_data: dict[str, Any] = {}
                with open(output_file, "r") as f:
                    output_data = json.load(f)

                status = output_data.get("status", "successful")
                output_args = json.dumps(output_data.get("output", {}))

                if status == "successful":
                    job_state = JobState.SUCCESSFUL
                    error = None
                    self.logger.process_execution("success", result.stdout.strip())
                else:
                    job_state = JobState.FAULTED
                    error_data: dict[str, Any] = output_data.get("error", {})
                    error = JobError(
                        code=error_data.get("code", "PYTHON.PROCESS_FAILED"),
                        title=error_data.get("title", "Process Failed"),
                        category=error_data.get("category", "USER"),
                        detail=error_data.get(
                            "detail", "Process completed with failure status"
                        ),
                    )
                    self.logger.process_execution("failed", error_data.get("detail"))
            else:
                # No output file, assume success
                job_state = JobState.SUCCESSFUL
                output_args = "{}"
                error = None
                self.logger.process_execution("success", result.stdout.strip())

            await self.orchestrator.submit_job_state(
                heartbeats=[
                    HeartbeatData(
                        robot_key=command.robot_key,
                        robot_state=SessionState.AVAILABLE,
                        process_key=command.data.process_key,
                        job_key=command.data.job_key,
                        job_state=job_state,
                        output_arguments=output_args,
                        error=error,
                    )
                ],
                license_key=self.license_key,
            )

        except subprocess.CalledProcessError as e:
            self.logger.process_execution("failed", e.stderr)
            await self.orchestrator.submit_job_state(
                heartbeats=[
                    HeartbeatData(
                        robot_key=command.robot_key,
                        robot_state=SessionState.AVAILABLE,
                        process_key=command.data.process_key,
                        job_key=command.data.job_key,
                        job_state=JobState.FAULTED,
                        error=JobError(
                            code="PYTHON.AGENT_EXECUTION_FAILED",
                            title="Agent Execution Failed",
                            category="SYSTEM",
                            detail=e.stderr,
                        ),
                    )
                ],
                license_key=self.license_key,
            )
        except Exception as e:
            self.logger.process_execution("failed", str(e))
            await self.orchestrator.submit_job_state(
                heartbeats=[
                    HeartbeatData(
                        robot_key=command.robot_key,
                        robot_state=SessionState.AVAILABLE,
                        process_key=command.data.process_key,
                        job_key=command.data.job_key,
                        job_state=JobState.FAULTED,
                        error=JobError(
                            code="PYTHON.AGENT_EXECUTION_FAILED",
                            title="Agent Execution Failed",
                            category="SYSTEM",
                            detail=str(e),
                        ),
                    )
                ],
                license_key=self.license_key,
            )

    async def process_commands(self, response: HeartbeatResponse) -> None:
        """Process commands from heartbeat response.

        Args:
            response: The heartbeat response containing commands
        """
        for command in response.commands:
            if command.data.type == "StartProcess":
                self.logger.job_start(
                    command.data.job_key,
                    command.data.package_id,
                    command.data.package_version,
                )

                # Download and setup package
                process_path = await self.download_and_setup_package(
                    command.data.package_id,
                    command.data.package_version,
                    command.data.feed_id,
                )

                if process_path:
                    # Execute the process asynchronously without blocking
                    asyncio.create_task(
                        self.execute_process(
                            process_path,
                            command,
                        )
                    )
                else:
                    self.logger.error("Failed to setup package")

    async def run(self) -> None:
        """Main loop: Initialize once, then send heartbeats every 10 seconds."""
        self.logger.section("UiPath Robot Service")

        if not await self.initialize():
            self.logger.error("Initialization failed")
            return

        assert self.license_key is not None

        await self.orchestrator.start_service(self.license_key)
        self.logger.success("Service started")

        self.logger.info(f"Listening for jobs (heartbeat: {self.heartbeat_interval}s)")

        try:
            while True:
                response = await self.orchestrator.heartbeat(self.license_key)
                self.logger.heartbeat()

                if response and response.commands:
                    await self.process_commands(response)

                await asyncio.sleep(self.heartbeat_interval)
        finally:
            self.logger.info("Stopping service...")
            await self.orchestrator.stop_service(self.license_key)


async def start_robot(verbose: bool = False) -> None:
    """Run the robot service.

    Args:
        verbose: Enable verbose logging
    """
    robot = Robot(verbose=verbose)
    await robot.run()


def main() -> None:
    """Main entry point for running the robot service."""
    import argparse

    parser = argparse.ArgumentParser(description="UiPath Robot Service")
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose logging",
    )
    args = parser.parse_args()

    load_dotenv()
    init_logger(verbose=args.verbose)

    try:
        asyncio.run(start_robot(verbose=args.verbose))
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()

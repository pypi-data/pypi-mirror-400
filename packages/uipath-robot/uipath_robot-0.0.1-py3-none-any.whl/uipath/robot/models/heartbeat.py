"""Models for the heartbeat response from Orchestrator."""

from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class JobState(str, Enum):
    """Job state enumeration."""

    PENDING = "Pending"
    RUNNING = "Running"
    SUCCESSFUL = "Successful"
    FAULTED = "Faulted"
    STOPPING = "Stopping"
    TERMINATING = "Terminating"
    STOPPED = "Stopped"
    SUSPENDED = "Suspended"
    RESUMED = "Resumed"


class SessionState(str, Enum):
    """Robot session state enumeration."""

    AVAILABLE = "Available"
    BUSY = "Busy"
    DISCONNECTED = "Disconnected"
    UNRESPONSIVE = "Unresponsive"


class ExecutionSettings(BaseModel):
    """Execution settings for the robot."""

    model_config = ConfigDict(extra="allow")


class AuthSettings(BaseModel):
    """Authentication settings for the robot."""

    model_config = ConfigDict(extra="allow")


class CommandData(BaseModel):
    """Data payload for a robot command."""

    model_config = ConfigDict(
        extra="allow", validate_by_name=True, validate_by_alias=True
    )

    process_settings: Any = Field(None, alias="processSettings")
    video_recording_settings: Any = Field(None, alias="videoRecordingSettings")
    package_id: str = Field(alias="packageId")
    package_version: str = Field(alias="packageVersion")
    target_framework: str = Field(alias="targetFramework")
    username: str | None = None
    password: str | None = None
    credential_connection_data: Any = Field(None, alias="credentialConnectionData")
    credential_type: int = Field(alias="credentialType")
    process_name: str = Field(alias="processName")
    persistence_id: str | None = Field(None, alias="persistenceId")
    resume_version: str | None = Field(None, alias="resumeVersion")
    resume_source: str | None = Field(None, alias="resumeSource")
    suspend_blob_type: str | None = Field(None, alias="suspendBlobType")
    input_arguments: str = Field(alias="inputArguments")
    input_file: str | None = Field(None, alias="inputFile")
    default_input_arguments: str | None = Field(None, alias="defaultInputArguments")
    environment_variables: str | None = Field(None, alias="environmentVariables")
    internal_arguments: str = Field(alias="internalArguments")
    entry_point_path: str = Field(alias="entryPointPath")
    feed_id: str | None = Field(alias="feedId")
    feed_url: str = Field(alias="feedUrl")
    requires_user_interaction: bool = Field(alias="requiresUserInteraction")
    source: str
    profiling_options: dict[str, Any] | None = Field(
        alias="profilingOptions", default=None
    )
    job_source: str = Field(alias="jobSource")
    job_key: str = Field(alias="jobKey")
    process_key: str = Field(alias="processKey")
    folder_id: int = Field(alias="folderId")
    fully_qualified_folder_name: str = Field(alias="fullyQualifiedFolderName")
    folder_key: str = Field(alias="folderKey")
    folder_path: str = Field(alias="folderPath")
    fps_context: Any = Field(None, alias="fpsContext")
    fps_properties: Any = Field(None, alias="fpsProperties")
    trace_id: str | None = Field(None, alias="traceId")
    parent_span_id: str | None = Field(None, alias="parentSpanId")
    root_span_id: str | None = Field(None, alias="rootSpanId")
    id: str
    type: str


class UserDetails(BaseModel):
    """User details associated with the command."""

    model_config = ConfigDict(extra="allow")

    key: str
    email: str


class Command(BaseModel):
    """Robot command from Orchestrator."""

    model_config = ConfigDict(
        extra="allow", validate_by_name=True, validate_by_alias=True
    )

    robot_key: str = Field(alias="robotKey")
    username: str | None = None
    robot_name: str = Field(alias="robotName")
    robot_type: int = Field(alias="robotType")
    machine_id: int = Field(alias="machineId")
    has_license: bool = Field(alias="hasLicense")
    is_external_licensed: bool = Field(alias="isExternalLicensed")
    execution_settings: ExecutionSettings = Field(alias="executionSettings")
    auth_settings: AuthSettings = Field(alias="authSettings")
    data: CommandData
    user_details: UserDetails = Field(alias="userDetails")


class HeartbeatResponse(BaseModel):
    """Response from the heartbeat endpoint containing robot commands."""

    model_config = ConfigDict(
        extra="allow", validate_by_name=True, validate_by_alias=True
    )

    commands: list[Command]
    service_settings_stamp: str = Field(alias="serviceSettingsStamp")
    is_unattended: bool = Field(alias="isUnattended")
    is_unattended_licensed: bool = Field(alias="isUnattendedLicensed")


class JobError(BaseModel):
    """Job error details."""

    model_config = ConfigDict(
        extra="allow", validate_by_name=True, validate_by_alias=True
    )

    code: str
    title: str
    category: str
    detail: str | None = None


class HeartbeatData(BaseModel):
    """Heartbeat data for job state submission."""

    model_config = ConfigDict(
        extra="allow", validate_by_name=True, validate_by_alias=True
    )

    robot_key: str = Field(alias="robotKey")
    job_state: JobState = Field(alias="jobState")
    job_key: str = Field(alias="jobKey")
    info: str | None = None
    process_key: str = Field(alias="processKey")
    output_arguments: str | None = Field(None, alias="outputArguments")
    robot_state: SessionState = Field(alias="robotState")
    error: JobError | None = Field(None, alias="error")
    trace_id: str | None = Field(None, alias="traceId")
    parent_span_id: str | None = Field(None, alias="parentSpanId")
    root_span_id: str | None = Field(None, alias="rootSpanId")

"""
Core types and interfaces for TestDino CLI
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Protocol

from pydantic import BaseModel, Field, HttpUrl


# CLI Options Schema (using Pydantic for validation like Zod)
class CLIOptions(BaseModel):
    """CLI options model with validation"""

    report_directory: str = Field(min_length=1, description="Report directory is required")
    token: str = Field(min_length=1, description="API token is required")
    environment: str = Field(default="unknown", description="Target environment tag")
    upload_images: bool = Field(default=False)
    upload_videos: bool = Field(default=False)
    upload_html: bool = Field(default=False)
    upload_traces: bool = Field(default=False)
    upload_files: bool = Field(default=False)
    upload_full_json: bool = Field(default=False)
    json_report: Optional[str] = None
    html_report: Optional[str] = None
    trace_dir: Optional[str] = None
    verbose: bool = Field(default=False)

    model_config = {"str_strip_whitespace": True}


# Configuration Schema
class Config(BaseModel):
    """Configuration model with validation"""

    api_url: HttpUrl
    token: str = Field(min_length=1)
    environment: str = Field(default="unknown")
    upload_images: bool = Field(default=False)
    upload_videos: bool = Field(default=False)
    upload_html: bool = Field(default=False)
    upload_traces: bool = Field(default=False)
    upload_files: bool = Field(default=False)
    upload_full_json: bool = Field(default=False)
    verbose: bool = Field(default=False)
    # Performance and upload settings
    batch_size: int = Field(default=5, ge=1, le=20)
    max_concurrent_uploads: int = Field(default=10, ge=1, le=50)
    upload_timeout: int = Field(default=60000, ge=5000, le=300000)
    retry_attempts: int = Field(default=3, ge=1, le=10)

    model_config = {"str_strip_whitespace": True}


# Error Types
class BaseError(Exception):
    """Base exception class for all custom errors"""

    def __init__(self, message: str, code: str, cause: Optional[Exception] = None):
        super().__init__(message)
        self.message = message
        self.code = code
        self.cause = cause


class ConfigurationError(BaseError):
    """Configuration related errors"""

    def __init__(self, message: str, cause: Optional[Exception] = None):
        super().__init__(message, "CONFIG_ERROR", cause)


class ValidationError(BaseError):
    """Validation related errors"""

    def __init__(self, message: str, cause: Optional[Exception] = None):
        super().__init__(message, "VALIDATION_ERROR", cause)


class NetworkError(BaseError):
    """Network related errors"""

    def __init__(self, message: str, cause: Optional[Exception] = None):
        super().__init__(message, "NETWORK_ERROR", cause)


class FileSystemError(BaseError):
    """File system related errors"""

    def __init__(self, message: str, cause: Optional[Exception] = None):
        super().__init__(message, "FILESYSTEM_ERROR", cause)


class AuthenticationError(BaseError):
    """Authentication related errors"""

    def __init__(self, message: str, cause: Optional[Exception] = None):
        super().__init__(message, "AUTH_ERROR", cause)


@dataclass
class UsageLimitData:
    """Usage limit error data from server response"""
    tier: str
    limit: int
    used: int
    remaining: int
    reset_date: str
    organization_id: Optional[str] = None


class UsageLimitError(BaseError):
    """Error thrown when monthly test case limit is exceeded"""

    def __init__(self, message: str, data: UsageLimitData, cause: Optional[Exception] = None):
        super().__init__(message, "USAGE_LIMIT_EXCEEDED", cause)
        self.data = data


# Exit Codes
class ExitCode(int, Enum):
    """Exit codes for the CLI"""

    SUCCESS = 0
    GENERAL_ERROR = 1
    AUTHENTICATION_ERROR = 2
    FILE_NOT_FOUND_ERROR = 3
    NETWORK_ERROR = 4
    USAGE_LIMIT_ERROR = 5


# Command Protocol
class Command(Protocol):
    """Command interface protocol"""

    name: str
    description: str

    async def execute(self, options: CLIOptions) -> None:
        """Execute the command with given options"""
        ...


# Progress Tracking Protocol
class ProgressTracker(Protocol):
    """Progress tracker interface protocol"""

    def start(self, message: str) -> None:
        """Start progress tracking with a message"""
        ...

    def update(self, message: str) -> None:
        """Update progress message"""
        ...

    def succeed(self, message: str) -> None:
        """Mark progress as successful"""
        ...

    def fail(self, message: str) -> None:
        """Mark progress as failed"""
        ...

    def warn(self, message: str) -> None:
        """Show a warning message"""
        ...


# Utility function to convert string to boolean
def string_to_boolean(value: Optional[str]) -> bool:
    """Convert string value to boolean"""
    if not value:
        return False
    return value.lower() in ["true", "1", "yes", "on"]


def validate_environment_format(environment: str) -> bool:
    """Validate environment format: lowercase alphanumeric with hyphens/underscores"""
    import re
    pattern = r'^[a-z0-9]+([_-][a-z0-9]+)*$'
    return bool(re.match(pattern, environment))


def resolve_environment_value(cli_env: Optional[str]) -> str:
    """Resolve environment value: CLI option > env var > default"""
    import os
    
    # Priority: CLI option > TESTDINO_TARGET_ENV > default
    environment = cli_env or os.getenv("TESTDINO_TARGET_ENV", "unknown")
    
    # Validate format
    if environment != "unknown" and not validate_environment_format(environment):
        raise ValidationError(
            f"Invalid environment format: '{environment}'. "
            "Must be lowercase alphanumeric with optional hyphens/underscores (e.g., 'staging', 'prod-us', 'qa_env')"
        )
    
    return environment


# Export all public types
__all__ = [
    "CLIOptions",
    "Config",
    "BaseError",
    "ConfigurationError",
    "ValidationError",
    "NetworkError",
    "FileSystemError",
    "AuthenticationError",
    "UsageLimitError",
    "UsageLimitData",
    "ExitCode",
    "Command",
    "ProgressTracker",
    "string_to_boolean",
    "validate_environment_format",
    "resolve_environment_value",
]

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Iterator, List, Optional

from pydantic import BaseModel, Field, HttpUrl


class MessageType(str, Enum):

    """Enumerates possible backend message categories."""

    NOTIFY_UPGRADE_VERSION = "notify_upgrade_version"
    NOTIFY_API_KEY_EXPIRING = "notify_api_key_expiring"
    NOTIFY_API_KEY_EXPIRED = "notify_api_key_expired"
    MAINTENANCE = "maintenance"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class BackendMessage(BaseModel):
    """Represents a notification emitted by the FinLens backend."""

    message: str = Field(..., description="Human readable message to display to the user.")
    type: MessageType = Field(
        MessageType.INFO,
        description="Category describing how the client should surface the message.",
    )
    doc_url: Optional[HttpUrl] = Field(
        None,
        description="Optional URL with more context or remediation instructions.",
    )

    def is_upgrade_notice(self) -> bool:
        return self.type == MessageType.NOTIFY_UPGRADE_VERSION


class ApiKeyMeta(BaseModel):
    """Metadata describing the current API key state returned by the backend."""

    api_key: str = Field(..., description="Echo of the API key that was validated.")
    is_active: bool = Field(..., description="Indicates whether the API key is currently active.")
    expires_at: Optional[datetime] = Field(
        None, description="Timestamp (ISO 8601) indicating when the API key expires."
    )
    max_requests_per_day: Optional[int] = Field(
        None, description="Daily request quota associated with the API key, if applicable."
    )
    requests_remaining: Optional[int] = Field(
        None, description="Number of requests remaining in the current quota window."
    )


class VersionInfo(BaseModel):
    """Represents the compatibility information between client and backend versions."""

    client_version: str = Field(..., description="Version of finlens currently running on the client.")
    backend_version: Optional[str] = Field(
        None,
        description="Latest version reported by the backend. None when the backend skips the check.",
    )
    minimum_supported_version: Optional[str] = Field(
        None, description="Lowest client version that remains supported by the backend."
    )

    def requires_upgrade(self) -> bool:
        if not self.backend_version:
            return False
        return self.backend_version != self.client_version

    def is_out_of_support(self) -> bool:
        if not self.minimum_supported_version:
            return False
        return self.client_version < self.minimum_supported_version


class ApiKeyValidationResponse(BaseModel):
    """Canonical schema describing the backend response for API key validation."""

    meta: ApiKeyMeta = Field(..., description="Metadata regarding the API key.")
    version: VersionInfo = Field(..., description="Compatibility information for finlens client versions.")
    messages: Optional[List[BackendMessage]] = Field(
        None, description="Optional notifications or instructions for the caller."
    )

    def iter_messages(self) -> Iterator[BackendMessage]:
        for message in self.messages or []:
            yield message

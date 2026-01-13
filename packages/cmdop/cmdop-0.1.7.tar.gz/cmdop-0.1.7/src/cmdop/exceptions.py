"""
CMDOP SDK Exception Hierarchy.

All SDK exceptions inherit from CMDOPError for easy catching.
Exceptions are organized by category: connection, auth, session, etc.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from grpc import RpcError


# =============================================================================
# Base Exception
# =============================================================================


class CMDOPError(Exception):
    """Base exception for all CMDOP SDK errors."""

    def __init__(self, message: str, *, cause: Exception | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.__cause__ = cause

    def __str__(self) -> str:
        if self.__cause__:
            return f"{self.message} (caused by: {self.__cause__})"
        return self.message


# =============================================================================
# Connection Errors
# =============================================================================


class ConnectionError(CMDOPError):
    """Base for connection-related errors."""


class AgentNotRunningError(ConnectionError):
    """Local agent is not running or not discoverable."""

    def __init__(self, message: str = "Agent not running") -> None:
        super().__init__(message)


class StalePortFileError(ConnectionError):
    """Discovery file exists but agent is unreachable (likely crashed)."""

    def __init__(self, discovery_path: str) -> None:
        self.discovery_path = discovery_path
        super().__init__(f"Stale discovery file at {discovery_path}")

    def cleanup(self) -> None:
        """Remove the stale discovery file."""
        import os

        try:
            os.remove(self.discovery_path)
        except OSError:
            pass


class ConnectionTimeoutError(ConnectionError):
    """Connection attempt timed out."""

    def __init__(self, timeout_seconds: float) -> None:
        self.timeout_seconds = timeout_seconds
        super().__init__(f"Connection timed out after {timeout_seconds}s")


class ConnectionLostError(ConnectionError):
    """Connection was lost during operation."""


# =============================================================================
# Authentication Errors
# =============================================================================


class AuthenticationError(CMDOPError):
    """Base for authentication errors."""


class InvalidAPIKeyError(AuthenticationError):
    """API key is invalid or expired."""

    def __init__(self, message: str = "Invalid API key") -> None:
        super().__init__(message)


class PermissionDeniedError(AuthenticationError):
    """Permission denied (e.g., UID mismatch on Unix socket)."""

    def __init__(
        self,
        message: str = "Permission denied",
        *,
        agent_uid: int | None = None,
        caller_uid: int | None = None,
    ) -> None:
        self.agent_uid = agent_uid
        self.caller_uid = caller_uid
        if agent_uid is not None and caller_uid is not None:
            message = f"{message} (agent UID: {agent_uid}, caller UID: {caller_uid})"
        super().__init__(message)


class TokenExpiredError(AuthenticationError):
    """Authentication token has expired."""


# =============================================================================
# Agent Errors
# =============================================================================


class AgentError(CMDOPError):
    """Base for agent-related errors."""


class AgentOfflineError(AgentError):
    """Target agent is not connected to cloud relay."""

    def __init__(self, agent_id: str | None = None) -> None:
        self.agent_id = agent_id
        msg = f"Agent {agent_id} is offline" if agent_id else "Agent is offline"
        super().__init__(msg)


class AgentBusyError(AgentError):
    """Agent is busy and cannot accept new requests."""


class FeatureNotAvailableError(AgentError):
    """Requested feature is not available in current mode."""

    def __init__(self, feature: str, mode: str) -> None:
        self.feature = feature
        self.mode = mode
        super().__init__(f"Feature '{feature}' is not available in {mode} mode")


# =============================================================================
# Session Errors
# =============================================================================


class SessionError(CMDOPError):
    """Base for session-related errors."""


class SessionNotFoundError(SessionError):
    """Terminal session not found."""

    def __init__(self, session_id: str) -> None:
        self.session_id = session_id
        super().__init__(f"Session not found: {session_id}")


class SessionClosedError(SessionError):
    """Attempted operation on a closed session."""

    def __init__(self, session_id: str) -> None:
        self.session_id = session_id
        super().__init__(f"Session is closed: {session_id}")


class SessionInterruptedError(SessionError):
    """Session was interrupted (connection lost mid-stream)."""

    def __init__(self, session_id: str) -> None:
        self.session_id = session_id
        super().__init__(f"Session interrupted: {session_id}")


# =============================================================================
# File Errors
# =============================================================================


class FileError(CMDOPError):
    """Base for file operation errors."""


class FileNotFoundError(FileError):
    """File or directory not found."""

    def __init__(self, path: str) -> None:
        self.path = path
        super().__init__(f"File not found: {path}")


class FilePermissionError(FileError):
    """Permission denied for file operation."""

    def __init__(self, path: str, operation: str) -> None:
        self.path = path
        self.operation = operation
        super().__init__(f"Permission denied: {operation} on {path}")


class FileTooLargeError(FileError):
    """File exceeds size limit."""

    def __init__(self, path: str, size_bytes: int, max_bytes: int) -> None:
        self.path = path
        self.size_bytes = size_bytes
        self.max_bytes = max_bytes
        super().__init__(
            f"File too large: {path} ({size_bytes} bytes, max {max_bytes})"
        )


# =============================================================================
# Rate Limiting
# =============================================================================


class RateLimitError(CMDOPError):
    """Rate limit exceeded."""

    def __init__(self, retry_after_seconds: float | None = None) -> None:
        self.retry_after_seconds = retry_after_seconds
        msg = "Rate limit exceeded"
        if retry_after_seconds:
            msg += f", retry after {retry_after_seconds}s"
        super().__init__(msg)


# =============================================================================
# gRPC Error Mapping
# =============================================================================


def from_grpc_error(error: RpcError) -> CMDOPError:
    """Convert gRPC error to SDK exception."""
    from grpc import StatusCode

    code = error.code()
    details = error.details() or str(error)

    mapping = {
        StatusCode.UNAUTHENTICATED: InvalidAPIKeyError(details),
        StatusCode.PERMISSION_DENIED: PermissionDeniedError(details),
        StatusCode.NOT_FOUND: SessionNotFoundError(details),
        StatusCode.UNAVAILABLE: AgentOfflineError(),
        StatusCode.DEADLINE_EXCEEDED: ConnectionTimeoutError(30.0),
        StatusCode.RESOURCE_EXHAUSTED: RateLimitError(),
        StatusCode.CANCELLED: SessionInterruptedError(details),
    }

    return mapping.get(code, CMDOPError(details, cause=error))

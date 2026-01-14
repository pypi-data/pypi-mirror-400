"""Custom exception classes for Janet CLI."""


class JanetCLIError(Exception):
    """Base exception for all CLI errors."""

    pass


class AuthenticationError(JanetCLIError):
    """Authentication failed or token expired."""

    pass


class OrganizationAccessError(JanetCLIError):
    """User doesn't have access to organization."""

    pass


class NetworkError(JanetCLIError):
    """Network request failed."""

    pass


class ConfigurationError(JanetCLIError):
    """Invalid configuration."""

    pass


class SyncError(JanetCLIError):
    """Sync operation failed."""

    pass


class TokenExpiredError(AuthenticationError):
    """Access token has expired."""

    pass


class InvalidTokenError(AuthenticationError):
    """Invalid or malformed token."""

    pass

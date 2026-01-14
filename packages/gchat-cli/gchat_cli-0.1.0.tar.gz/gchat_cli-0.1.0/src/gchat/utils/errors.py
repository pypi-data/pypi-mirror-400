"""Custom exceptions for gchat."""


class GChatError(Exception):
    """Base exception for gchat."""

    exit_code = 1


class AuthenticationError(GChatError):
    """Authentication failed."""

    exit_code = 2


class NetworkError(GChatError):
    """Network request failed."""

    exit_code = 3


class ConfigurationError(GChatError):
    """Configuration is invalid or missing."""

    exit_code = 4


class AccountNotFoundError(GChatError):
    """Specified account does not exist."""

    exit_code = 5


class SpaceNotFoundError(GChatError):
    """Specified space does not exist."""

    exit_code = 6


class NoActiveAccountError(GChatError):
    """No active account is configured."""

    exit_code = 7

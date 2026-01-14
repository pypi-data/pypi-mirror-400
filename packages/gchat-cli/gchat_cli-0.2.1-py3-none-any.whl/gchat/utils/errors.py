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

    @classmethod
    def from_exception(cls, exc: Exception, context: str = "") -> "NetworkError":
        """Create a NetworkError with helpful messaging based on the exception type."""
        exc_str = str(exc).lower()
        exc_type = type(exc).__name__

        # DNS resolution failures
        if any(
            hint in exc_str
            for hint in ["getaddrinfo", "name or service not known", "nodename nor servname"]
        ):
            hostname = _extract_hostname(exc_str)
            msg = f"DNS resolution failed for '{hostname}'"
            if hostname and "googleapis.com" in hostname:
                msg += (
                    "\n\nTroubleshooting tips:"
                    "\n  • Try: sudo dscacheutil -flushcache (macOS)"
                    "\n         or resolvectl flush-caches (Linux)"
                    "\n  • Check if a VPN is interfering with DNS"
                    "\n  • Run: gchat doctor  (to diagnose connectivity)"
                )
            return DNSError(msg)

        # Connection refused / timeout
        if any(hint in exc_str for hint in ["connection refused", "errno 111"]):
            return NetworkError(
                f"Connection refused{': ' + context if context else ''}. "
                "The server may be down or blocked by a firewall."
            )

        if any(hint in exc_str for hint in ["timed out", "timeout", "errno 110"]):
            return NetworkError(
                f"Connection timed out{': ' + context if context else ''}. "
                "Check your internet connection or try again."
            )

        # SSL/TLS errors
        if any(hint in exc_str for hint in ["ssl", "certificate", "handshake"]):
            return NetworkError(
                f"SSL/TLS error{': ' + context if context else ''}. "
                "This may indicate a network proxy or certificate issue."
            )

        # Generic network error
        prefix = f"{context}: " if context else ""
        return cls(f"{prefix}{exc_type}: {exc}")


class DNSError(NetworkError):
    """DNS resolution failed."""

    pass


def _extract_hostname(error_str: str) -> str:
    """Try to extract hostname from error message."""
    import re

    # Common patterns for hostnames in error messages
    patterns = [
        r"getaddrinfo.*?'([^']+)'",
        r"host[= ]+([a-zA-Z0-9.-]+\.com)",
        r"([a-zA-Z0-9.-]+\.googleapis\.com)",
    ]
    for pattern in patterns:
        match = re.search(pattern, error_str)
        if match:
            return match.group(1)
    return ""


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

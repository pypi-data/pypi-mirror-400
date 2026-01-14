"""Network utilities including retry logic and diagnostics."""

import socket
import time
from collections.abc import Callable
from typing import TypeVar

from gchat.utils.errors import NetworkError

T = TypeVar("T")

# Endpoints to test for connectivity diagnostics
DIAGNOSTIC_ENDPOINTS = [
    ("google.com", 443, "General internet"),
    ("oauth2.googleapis.com", 443, "OAuth2 (authentication)"),
    ("www.googleapis.com", 443, "Google APIs"),
    ("chat.googleapis.com", 443, "Google Chat API"),
]


def retry_on_network_error(
    func: Callable[[], T],
    max_attempts: int = 3,
    base_delay: float = 0.5,
    max_delay: float = 4.0,
    context: str = "",
) -> T:
    """Retry a function on network errors with exponential backoff.

    Args:
        func: Function to call (should take no arguments)
        max_attempts: Maximum number of attempts (default: 3)
        base_delay: Initial delay in seconds (default: 0.5)
        max_delay: Maximum delay between retries (default: 4.0)
        context: Context for error messages

    Returns:
        The result of the function call

    Raises:
        NetworkError: If all attempts fail
    """
    last_exception: Exception | None = None

    for attempt in range(max_attempts):
        try:
            return func()
        except Exception as e:
            last_exception = e

            # Don't retry on non-network errors
            if not _is_retryable_error(e):
                raise NetworkError.from_exception(e, context)

            # Don't sleep after the last attempt
            if attempt < max_attempts - 1:
                delay = min(base_delay * (2**attempt), max_delay)
                time.sleep(delay)

    # All attempts failed
    raise NetworkError.from_exception(last_exception, context)  # type: ignore[arg-type]


def _is_retryable_error(exc: Exception) -> bool:
    """Check if an exception is a retryable network error."""
    exc_str = str(exc).lower()
    exc_type = type(exc).__name__.lower()

    # Retryable conditions
    retryable_hints = [
        "timeout",
        "timed out",
        "connection reset",
        "connection refused",
        "temporary failure",
        "try again",
        "service unavailable",
        "503",
        "502",
        "504",
        "getaddrinfo",  # DNS failures can be transient
    ]

    # Check exception message
    if any(hint in exc_str for hint in retryable_hints):
        return True

    # Check exception type
    if any(hint in exc_type for hint in ["timeout", "connection", "network"]):
        return True

    # Check for specific exception types
    if isinstance(exc, (TimeoutError, ConnectionError, OSError)):
        return True

    return False


def check_connectivity(timeout: float = 5.0) -> list[dict]:
    """Check connectivity to required endpoints.

    Args:
        timeout: Connection timeout in seconds

    Returns:
        List of diagnostic results for each endpoint
    """
    results = []

    for hostname, port, description in DIAGNOSTIC_ENDPOINTS:
        result = {
            "hostname": hostname,
            "port": port,
            "description": description,
            "success": False,
            "error": None,
            "latency_ms": None,
        }

        try:
            start = time.time()
            sock = socket.create_connection((hostname, port), timeout=timeout)
            sock.close()
            result["success"] = True
            result["latency_ms"] = round((time.time() - start) * 1000, 1)
        except socket.gaierror as e:
            result["error"] = f"DNS resolution failed: {e}"
        except TimeoutError:
            result["error"] = f"Connection timed out after {timeout}s"
        except OSError as e:
            result["error"] = str(e)

        results.append(result)

    return results


def get_dns_servers() -> list[str]:
    """Get the system's configured DNS servers (best effort)."""
    servers = []

    # Try reading resolv.conf (Linux/macOS)
    try:
        with open("/etc/resolv.conf") as f:
            for line in f:
                if line.strip().startswith("nameserver"):
                    parts = line.split()
                    if len(parts) >= 2:
                        servers.append(parts[1])
    except (FileNotFoundError, PermissionError):
        pass

    return servers

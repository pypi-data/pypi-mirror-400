"""
Clouditia SDK Exceptions

This module defines all exceptions that can be raised by the Clouditia SDK.
"""


class ClouditiaError(Exception):
    """
    Base exception for all Clouditia SDK errors.

    All other Clouditia exceptions inherit from this class,
    so you can catch all SDK errors with a single except clause.

    Example:
        >>> try:
        ...     result = session.run("some code")
        ... except ClouditiaError as e:
        ...     print(f"Clouditia error: {e}")
    """
    pass


class AuthenticationError(ClouditiaError):
    """
    Raised when API key authentication fails.

    This can happen when:
    - The API key is invalid or malformed
    - The API key has been revoked
    - The API key has expired

    Example:
        >>> try:
        ...     session = GPUSession("invalid_key")
        ...     session.verify()
        ... except AuthenticationError:
        ...     print("Invalid API key")
    """
    pass


class SessionError(ClouditiaError):
    """
    Raised when there's a problem with the GPU session.

    This can happen when:
    - The session is not running (stopped, terminated)
    - The session pod is not found
    - The session is not accessible

    Example:
        >>> try:
        ...     result = session.run("print('hello')")
        ... except SessionError as e:
        ...     print(f"Session problem: {e}")
    """
    pass


class ExecutionError(ClouditiaError):
    """
    Raised when code execution fails on the remote GPU.

    This can happen when:
    - Python code raises an exception
    - Shell command returns non-zero exit code
    - There's a runtime error during execution

    The error message contains details about what went wrong.

    Example:
        >>> try:
        ...     result = session.run("raise ValueError('test')")
        ... except ExecutionError as e:
        ...     print(f"Execution failed: {e}")
    """
    pass


class TimeoutError(ClouditiaError):
    """
    Raised when an operation times out.

    This can happen when:
    - Synchronous code execution exceeds the timeout limit
    - Network request times out
    - Async job polling exceeds the specified timeout

    For long-running tasks, consider using async jobs with session.submit().

    Example:
        >>> try:
        ...     result = session.run("time.sleep(300)", timeout=60)
        ... except TimeoutError:
        ...     print("Operation timed out, consider using async jobs")
    """
    pass


class CommandBlockedError(ClouditiaError):
    """
    Raised when a shell command is blocked by security filters.

    Clouditia has security filters that block potentially dangerous commands.
    Some commands may be blacklisted for security reasons.

    Example:
        >>> try:
        ...     result = session.shell("rm -rf /")
        ... except CommandBlockedError as e:
        ...     print(f"Command blocked: {e}")
    """
    pass

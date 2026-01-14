"""
Clouditia SDK - Execute Python and Shell code on remote GPU sessions.

This SDK provides a simple interface to interact with Clouditia GPU sessions,
allowing you to run Python code, shell commands, and long-running async jobs
on remote GPU-powered containers.

Basic Usage:
    >>> from clouditia import GPUSession
    >>> session = GPUSession("your_api_key")
    >>> result = session.run("print('Hello from GPU!')")
    >>> print(result.output)
    Hello from GPU!

For more examples, see: https://clouditia.com/docs
"""

__version__ = "1.4.0"
__author__ = "Aina KIKI-SAGBE"
__email__ = "support@clouditia.com"

from .client import GPUSession, connect
from .jobs import AsyncJob
from .results import ExecutionResult
from .exceptions import (
    ClouditiaError,
    AuthenticationError,
    SessionError,
    ExecutionError,
    TimeoutError,
    CommandBlockedError
)

# Jupyter magic loader
def load_ipython_extension(ipython):
    """Load the Clouditia Jupyter magic extension."""
    from .magic import load_ipython_extension as load_magic
    load_magic(ipython)

__all__ = [
    # Main classes
    "GPUSession",
    "AsyncJob",
    "ExecutionResult",
    # Convenience functions
    "connect",
    "load_ipython_extension",
    # Exceptions
    "ClouditiaError",
    "AuthenticationError",
    "SessionError",
    "ExecutionError",
    "TimeoutError",
    "CommandBlockedError",
    # Version info
    "__version__",
]

"""
Clouditia SDK Results

This module defines result classes returned by SDK operations.
"""

from typing import Any, Optional


class ExecutionResult:
    """
    Result of a code execution on the remote GPU.

    This class encapsulates the output, errors, and status of an execution.
    It can be used as a boolean to check if execution was successful.

    Attributes:
        output (str): Standard output from the execution (print statements, etc.)
        result (Any): The last evaluated expression (if any)
        error (str): Error message if execution failed
        exit_code (int): Exit code (0 = success, non-zero = failure)
        success (bool): True if execution completed successfully

    Example:
        >>> result = session.run("print('hello')")
        >>> if result:
        ...     print(result.output)  # "hello"
        ... else:
        ...     print(f"Error: {result.error}")

        >>> result = session.run("2 + 2")
        >>> print(result.result)  # "4"
    """

    def __init__(
        self,
        output: str = "",
        result: Any = None,
        error: str = "",
        exit_code: int = 0,
        success: bool = True
    ):
        """
        Initialize an ExecutionResult.

        Args:
            output: Standard output from execution
            result: Last evaluated expression
            error: Error message if failed
            exit_code: Process exit code
            success: Whether execution succeeded
        """
        self.output = output
        self.result = result
        self.error = error
        self.exit_code = exit_code
        self.success = success

    def __repr__(self) -> str:
        """Return a string representation of the result."""
        if self.success:
            preview = self.output[:50] if self.output else ""
            return f"ExecutionResult(success=True, output={preview!r}{'...' if len(self.output) > 50 else ''})"
        else:
            preview = self.error[:50] if self.error else ""
            return f"ExecutionResult(success=False, error={preview!r}{'...' if len(self.error) > 50 else ''})"

    def __bool__(self) -> bool:
        """
        Allow using the result as a boolean.

        Returns:
            True if execution was successful, False otherwise.

        Example:
            >>> if session.run("print('test')"):
            ...     print("Success!")
        """
        return self.success

    def __str__(self) -> str:
        """Return the output or error as a string."""
        if self.success:
            return self.output
        else:
            return f"Error: {self.error}"

    def raise_for_status(self) -> None:
        """
        Raise an exception if the execution failed.

        Raises:
            ExecutionError: If the execution was not successful.

        Example:
            >>> result = session.run("some_code")
            >>> result.raise_for_status()  # Raises if failed
        """
        if not self.success:
            from .exceptions import ExecutionError
            raise ExecutionError(self.error)

    def to_dict(self) -> dict:
        """
        Convert the result to a dictionary.

        Returns:
            Dict with output, result, error, exit_code, and success keys.
        """
        return {
            "output": self.output,
            "result": self.result,
            "error": self.error,
            "exit_code": self.exit_code,
            "success": self.success
        }

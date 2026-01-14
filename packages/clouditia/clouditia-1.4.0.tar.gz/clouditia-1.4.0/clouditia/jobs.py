"""
Clouditia SDK - Async Jobs

This module provides the AsyncJob class for managing long-running tasks.
"""

import time
from typing import Optional, Dict, TYPE_CHECKING

from .results import ExecutionResult
from .exceptions import ClouditiaError, TimeoutError

if TYPE_CHECKING:
    from .client import GPUSession


class AsyncJob:
    """
    Represents an asynchronous job running on a remote GPU.

    Async jobs are ideal for long-running tasks like model training
    that can take hours or even days. They run in the background
    and you can check their status, view logs, and retrieve results.

    You typically don't create AsyncJob instances directly - they are
    returned by session.submit().

    Attributes:
        job_id (str): Unique identifier for the job
        name (str): Optional name for the job
        session (GPUSession): Parent session

    Example:
        >>> job = session.submit('''
        ... for epoch in range(100):
        ...     print(f"Epoch {epoch}")
        ...     # training code...
        ... ''', name="training")
        >>>
        >>> # Check status
        >>> print(job.status())  # "running"
        >>>
        >>> # View logs in real-time
        >>> while not job.is_done():
        ...     print(job.logs(new_only=True))
        ...     time.sleep(10)
        >>>
        >>> # Get final result
        >>> result = job.result()
        >>> print(result.output)
    """

    def __init__(
        self,
        session: "GPUSession",
        job_id: str,
        name: Optional[str] = None,
        _data: Optional[Dict] = None
    ):
        """
        Initialize an AsyncJob.

        Args:
            session: Parent GPUSession
            job_id: Unique job identifier
            name: Optional job name
            _data: Internal data from API response
        """
        self.session = session
        self.job_id = job_id
        self.name = name
        self._data = _data or {}
        self._last_log_lines = 0

    def status(self) -> str:
        """
        Get the current status of the job.

        Returns:
            One of: "pending", "running", "completed", "failed", "cancelled"

        Example:
            >>> if job.status() == "running":
            ...     print("Job is still running...")
        """
        import requests

        response = requests.get(
            f"{self.session.base_url}/api/jobs/status/",
            headers=self.session._headers(),
            params={"job_id": self.job_id},
            timeout=30
        )

        data = self.session._check_response(response)
        self._data = data
        return data.get("status", "unknown")

    def is_done(self) -> bool:
        """
        Check if the job has finished (success, failure, or cancelled).

        Returns:
            True if job is no longer running, False otherwise.

        Example:
            >>> while not job.is_done():
            ...     time.sleep(30)
            >>> print("Job finished!")
        """
        status = self.status()
        return status in ("completed", "failed", "cancelled")

    def is_running(self) -> bool:
        """
        Check if the job is currently running.

        Returns:
            True if job status is "running".
        """
        return self.status() == "running"

    def is_pending(self) -> bool:
        """
        Check if the job is waiting to start.

        Returns:
            True if job status is "pending".
        """
        return self.status() == "pending"

    def logs(self, tail: int = 50, new_only: bool = False) -> str:
        """
        Retrieve logs from the running job.

        This allows you to monitor progress in real-time during execution.

        Args:
            tail: Number of last lines to retrieve (default: 50, max: 1000)
            new_only: If True, only return lines not seen in previous calls

        Returns:
            Log output as a string.

        Example:
            >>> # Show all recent logs
            >>> print(job.logs(tail=100))

            >>> # Show only new logs since last call
            >>> while job.is_running():
            ...     new_logs = job.logs(new_only=True)
            ...     if new_logs.strip():
            ...         print(new_logs, end='')
            ...     time.sleep(5)
        """
        import requests

        response = requests.get(
            f"{self.session.base_url}/api/jobs/logs/",
            headers=self.session._headers(),
            params={"job_id": self.job_id, "tail": tail},
            timeout=30
        )

        data = self.session._check_response(response)
        logs = data.get("logs", "")

        if new_only:
            lines = logs.split("\n")
            new_lines = lines[self._last_log_lines:]
            self._last_log_lines = len(lines)
            return "\n".join(new_lines)

        return logs

    def result(self) -> ExecutionResult:
        """
        Get the final result of the job.

        This should only be called after the job has completed.
        Use is_done() to check if the job has finished.

        Returns:
            ExecutionResult with output, error, and exit_code.

        Raises:
            ClouditiaError: If job is not yet completed.

        Example:
            >>> job.wait()  # Wait for completion
            >>> result = job.result()
            >>> if result.success:
            ...     print(result.output)
            ... else:
            ...     print(f"Failed: {result.error}")
        """
        import requests

        response = requests.get(
            f"{self.session.base_url}/api/jobs/result/",
            headers=self.session._headers(),
            params={"job_id": self.job_id},
            timeout=30
        )

        data = self.session._check_response(response)

        return ExecutionResult(
            output=data.get("output", ""),
            result=None,
            error=data.get("error", ""),
            exit_code=data.get("exit_code", 0),
            success=data.get("status") == "completed"
        )

    def cancel(self) -> bool:
        """
        Cancel the job if it's still running.

        Returns:
            True if cancellation was successful.

        Example:
            >>> if job.is_running():
            ...     job.cancel()
            ...     print("Job cancelled")
        """
        import requests

        response = requests.post(
            f"{self.session.base_url}/api/jobs/cancel/",
            headers=self.session._headers(),
            json={"job_id": self.job_id},
            timeout=30
        )

        data = self.session._check_response(response)
        return data.get("success", False)

    def wait(
        self,
        timeout: Optional[int] = None,
        poll_interval: Optional[int] = None,
        show_logs: bool = False
    ) -> ExecutionResult:
        """
        Wait for the job to complete and return the result.

        This is a blocking call that polls the job status until it finishes.

        Args:
            timeout: Maximum time to wait in seconds (None = wait forever)
            poll_interval: How often to check status in seconds (default: 5)
            show_logs: If True, print logs to stdout during wait

        Returns:
            ExecutionResult when job completes.

        Raises:
            TimeoutError: If timeout is reached before job completes.

        Example:
            >>> # Wait with live log output
            >>> result = job.wait(show_logs=True)

            >>> # Wait with timeout
            >>> try:
            ...     result = job.wait(timeout=3600)  # 1 hour max
            ... except TimeoutError:
            ...     job.cancel()
        """
        poll_interval = poll_interval or self.session.poll_interval
        start_time = time.time()

        while True:
            if timeout and (time.time() - start_time) > timeout:
                raise TimeoutError(f"Job did not complete within {timeout} seconds")

            if show_logs:
                logs = self.logs(new_only=True)
                if logs.strip():
                    print(logs, end="")

            if self.is_done():
                break

            time.sleep(poll_interval)

        return self.result()

    def get_info(self) -> Dict:
        """
        Get detailed information about the job.

        Returns:
            Dict with job details including status, timestamps, duration, etc.

        Example:
            >>> info = job.get_info()
            >>> print(f"Duration: {info.get('duration_seconds', 0):.1f}s")
        """
        self.status()  # Refresh _data
        return self._data.copy()

    @property
    def duration(self) -> Optional[float]:
        """
        Get the job duration in seconds.

        Returns:
            Duration in seconds, or None if not available.
        """
        self.status()  # Refresh _data
        return self._data.get("duration_seconds")

    def __repr__(self) -> str:
        """Return string representation of the job."""
        name_str = f", name={self.name!r}" if self.name else ""
        return f"AsyncJob(id={self.job_id!r}{name_str})"

    def __str__(self) -> str:
        """Return a human-readable string."""
        status = self._data.get("status", "unknown")
        name = self.name or self.job_id[:8]
        return f"Job '{name}' ({status})"

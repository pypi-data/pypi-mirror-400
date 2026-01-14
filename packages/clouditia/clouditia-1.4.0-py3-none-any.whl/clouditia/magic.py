"""
Clouditia SDK - Jupyter Magic

This module provides Jupyter/IPython magic commands for Clouditia.

Usage in Jupyter:
    # Load the extension
    %load_ext clouditia

    # Set your API key
    CLOUDITIA_API_KEY = "ck_your_api_key"

    # Run code on GPU
    %%clouditia
    import torch
    print(torch.cuda.is_available())

    # Or specify the key directly
    %%clouditia ck_your_api_key
    print("Hello from GPU!")

    # Async mode for long tasks
    %%clouditia --async
    for epoch in range(100):
        train()
"""

from typing import Optional

# Global session cache
_current_session: Optional["GPUSession"] = None


def load_ipython_extension(ipython):
    """
    Load the Clouditia IPython/Jupyter extension.

    This function is called automatically when you run:
        %load_ext clouditia

    It registers the %%clouditia cell magic.
    """
    from IPython.core.magic import register_cell_magic, register_line_magic
    from .client import GPUSession

    global _current_session

    @register_cell_magic
    def clouditia(line, cell):
        """
        Execute a cell on a remote Clouditia GPU session.

        Usage:
            %%clouditia
            # Your Python code here
            import torch
            print(torch.cuda.is_available())

        With API key:
            %%clouditia ck_your_api_key
            print("Hello!")

        Async mode (for long-running tasks):
            %%clouditia --async
            for epoch in range(100):
                train()

        Options:
            --async     Submit as async job instead of waiting
            --timeout N Set timeout in seconds (default: 120)
        """
        global _current_session

        # Parse line arguments
        args = line.strip().split()
        api_key = None
        async_mode = False
        timeout = 120

        i = 0
        while i < len(args):
            arg = args[i]
            if arg == "--async":
                async_mode = True
            elif arg == "--timeout" and i + 1 < len(args):
                i += 1
                try:
                    timeout = int(args[i])
                except ValueError:
                    print(f"Invalid timeout value: {args[i]}")
                    return
            elif arg.startswith("ck_") or arg.startswith("sk_"):
                api_key = arg
            i += 1

        # Get or create session
        if api_key:
            _current_session = GPUSession(api_key, timeout=timeout)
        elif _current_session is None:
            # Look for API key in user namespace
            user_ns = ipython.user_ns
            if "CLOUDITIA_API_KEY" in user_ns:
                _current_session = GPUSession(
                    user_ns["CLOUDITIA_API_KEY"],
                    timeout=timeout
                )
            elif "clouditia_api_key" in user_ns:
                _current_session = GPUSession(
                    user_ns["clouditia_api_key"],
                    timeout=timeout
                )
            else:
                print("Error: No API key found.")
                print("")
                print("Set your API key first:")
                print("  CLOUDITIA_API_KEY = 'ck_your_api_key'")
                print("")
                print("Or pass it directly:")
                print("  %%clouditia ck_your_api_key")
                return

        # Execute the cell
        try:
            if async_mode:
                job = _current_session.submit(cell)
                print(f"Job submitted: {job.job_id}")
                print(f"Use _clouditia_job.status() to check status")
                print(f"Use _clouditia_job.logs() to view logs")
                ipython.user_ns["_clouditia_job"] = job
                return job
            else:
                result = _current_session.run(cell, timeout=timeout)

                if result.output:
                    print(result.output, end="")

                if result.error:
                    print(f"\nError: {result.error}")

                if result.result is not None:
                    return result.result

        except Exception as e:
            print(f"Clouditia error: {e}")
            return None

    @register_line_magic
    def clouditia_status(line):
        """
        Check the status of the current Clouditia session.

        Usage:
            %clouditia_status
        """
        global _current_session

        if _current_session is None:
            print("No active session. Use %%clouditia first.")
            return

        try:
            info = _current_session.verify()
            print(f"Session: {info.get('session_name', 'Unknown')}")
            print(f"GPU: {info.get('gpu_type', 'Unknown')}")
            print(f"Status: {info.get('status', 'Unknown')}")
            print(f"Credit: {info.get('user_credit', 0)}€")
        except Exception as e:
            print(f"Error checking status: {e}")

    @register_line_magic
    def clouditia_jobs(line):
        """
        List recent Clouditia jobs.

        Usage:
            %clouditia_jobs
            %clouditia_jobs running
        """
        global _current_session

        if _current_session is None:
            print("No active session. Use %%clouditia first.")
            return

        status_filter = line.strip() if line.strip() else None

        try:
            jobs = _current_session.jobs(status=status_filter, limit=10)

            if not jobs:
                print("No jobs found.")
                return

            print(f"{'ID':<10} {'Name':<20} {'Status':<12} {'Duration':<10}")
            print("-" * 55)

            for job in jobs:
                job_id = job.job_id[:8]
                name = (job.name or "-")[:18]
                status = job._data.get("status", "unknown")
                duration = job._data.get("duration_seconds", 0)
                dur_str = f"{duration:.1f}s" if duration else "-"

                print(f"{job_id:<10} {name:<20} {status:<12} {dur_str:<10}")

        except Exception as e:
            print(f"Error listing jobs: {e}")

    print("Clouditia magic loaded!")
    print("")
    print("Usage:")
    print("  %%clouditia           - Run cell on GPU")
    print("  %%clouditia --async   - Submit as background job")
    print("  %clouditia_status     - Check session status")
    print("  %clouditia_jobs       - List recent jobs")
    print("")
    print("Set your API key:")
    print("  CLOUDITIA_API_KEY = 'ck_your_api_key'")


def unload_ipython_extension(ipython):
    """Unload the extension."""
    global _current_session
    _current_session = None
    print("Clouditia magic unloaded.")

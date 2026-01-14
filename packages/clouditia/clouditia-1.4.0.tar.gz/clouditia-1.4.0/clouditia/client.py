"""
Clouditia SDK - Main Client

This module provides the GPUSession class for interacting with remote GPU sessions.
"""

import base64
import inspect
import io
import json
import os
import pickle
import tarfile
import textwrap
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union

import requests

from .exceptions import (
    AuthenticationError,
    ClouditiaError,
    CommandBlockedError,
    ExecutionError,
    SessionError,
    TimeoutError,
)
from .jobs import AsyncJob
from .results import ExecutionResult


class GPUSession:
    """
    Main class for interacting with a Clouditia GPU session.

    A GPUSession represents a connection to a remote GPU-powered container.
    You can execute Python code, run shell commands, and manage long-running
    async jobs through this interface.

    Attributes:
        api_key (str): Your Clouditia API key
        base_url (str): Base URL of the Clouditia API
        timeout (int): Default timeout for synchronous operations (seconds)
        poll_interval (int): Interval for polling async jobs (seconds)

    Example:
        >>> from clouditia import GPUSession
        >>>
        >>> # Create a session
        >>> session = GPUSession("ck_your_api_key_here")
        >>>
        >>> # Execute Python code
        >>> result = session.run("print('Hello from GPU!')")
        >>> print(result.output)
        Hello from GPU!
        >>>
        >>> # Execute shell commands
        >>> result = session.shell("ls -la")
        >>> print(result.output)
        >>>
        >>> # Submit long-running jobs
        >>> job = session.submit("train_model()", name="training")
        >>> job.wait(show_logs=True)
    """

    DEFAULT_BASE_URL = "https://clouditia.com/code-editor"

    def __init__(
        self,
        api_key: str,
        base_url: Optional[str] = None,
        timeout: int = 120,
        poll_interval: int = 5
    ):
        """
        Initialize a GPU session.

        Args:
            api_key: Your Clouditia API key (starts with 'ck_' or 'sk_')
            base_url: Base URL of the API (default: https://clouditia.com/code-editor)
            timeout: Default timeout for synchronous operations in seconds
            poll_interval: Interval for polling async job status in seconds

        Example:
            >>> session = GPUSession("ck_abc123...")
            >>> session = GPUSession("ck_abc123...", timeout=300)
        """
        if not api_key:
            raise AuthenticationError("API key is required")

        self.api_key = api_key
        self.base_url = (base_url or self.DEFAULT_BASE_URL).rstrip("/")
        self.timeout = timeout
        self.poll_interval = poll_interval
        self._session_info: Optional[Dict] = None
        self._remote_vars: Dict[str, bool] = {}
        self._persistent_id: Optional[str] = None  # ID de session persistante

    def _headers(self) -> Dict[str, str]:
        """Get headers with authentication."""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def _check_response(self, response: requests.Response) -> Dict:
        """Check response and raise appropriate exceptions."""
        try:
            data = response.json()
        except json.JSONDecodeError:
            raise ClouditiaError(f"Invalid JSON response: {response.text[:200]}")

        if response.status_code == 401:
            raise AuthenticationError(data.get("error", "Invalid API key"))
        elif response.status_code == 403:
            error_msg = data.get("error", "Access forbidden")
            if "blocked" in error_msg.lower() or "blacklist" in error_msg.lower():
                raise CommandBlockedError(error_msg)
            raise SessionError(error_msg)
        elif response.status_code == 404:
            raise SessionError(data.get("error", "Resource not found"))
        elif response.status_code >= 400:
            raise ClouditiaError(data.get("error", f"HTTP {response.status_code}"))

        if not data.get("success", True):
            error = data.get("error", "Unknown error")
            if "timeout" in error.lower():
                raise TimeoutError(error)
            if "blocked" in error.lower():
                raise CommandBlockedError(error)
            raise ExecutionError(error)

        return data

    def verify(self) -> Dict:
        """
        Verify the API key and get session information.

        Returns:
            Dict containing session_id, gpu_type, status, URLs, and billing info.

        Raises:
            AuthenticationError: If API key is invalid
            SessionError: If session is not active

        Example:
            >>> info = session.verify()
            >>> print(f"GPU: {info['gpu_type']}")
            >>> print(f"Credit: {info['user_credit']}€")
        """
        response = requests.get(
            f"{self.base_url}/api/verify/",
            headers=self._headers(),
            timeout=30
        )
        data = self._check_response(response)
        self._session_info = data
        return data

    def start(self) -> bool:
        """
        Start a persistent Python session on the remote GPU.

        After calling start(), all run() calls will share the same Python
        environment, preserving variables between executions until stop() is called.

        Returns:
            True if session started successfully.

        Raises:
            SessionError: If session cannot be started.

        Example:
            >>> session.start()
            >>> session.run("a = 2")
            >>> session.run("b = a * 5")
            >>> session.run("print(b)")  # prints: 10
            >>> session.stop()
        """
        response = requests.post(
            f"{self.base_url}/api/session/start/",
            headers=self._headers(),
            timeout=30
        )

        data = self._check_response(response)

        if data.get("success"):
            self._persistent_id = data.get("persistent_id")
            return True
        else:
            raise SessionError(data.get("error", "Failed to start persistent session"))

    def stop(self) -> bool:
        """
        Stop the persistent Python session.

        After calling stop(), variables are no longer preserved between run() calls.

        Returns:
            True if session stopped successfully.

        Example:
            >>> session.start()
            >>> session.run("x = 100")
            >>> session.stop()
            >>> session.run("print(x)")  # Error: x not defined
        """
        if not self._persistent_id:
            return True  # No session to stop

        response = requests.post(
            f"{self.base_url}/api/session/stop/",
            headers=self._headers(),
            json={"persistent_id": self._persistent_id},
            timeout=30
        )

        self._persistent_id = None

        try:
            data = self._check_response(response)
            return data.get("success", True)
        except:
            return True  # Session might already be stopped

    @property
    def is_persistent(self) -> bool:
        """Check if a persistent session is active."""
        return self._persistent_id is not None

    def run(
        self,
        code: str,
        timeout: Optional[int] = None,
        stream: bool = True
    ) -> ExecutionResult:
        """
        Execute Python code on the remote GPU.

        Behavior depends on whether a persistent session is active:
        - With start(): Variables persist between run() calls
        - Without start(): Each run() is isolated (default)

        By default, output is streamed in real-time to stdout.
        Set stream=False for silent execution.

        Args:
            code: Python code to execute
            timeout: Timeout in seconds (default: self.timeout)
            stream: If True (default), print output in real-time

        Returns:
            ExecutionResult with output, result, and status.

        Raises:
            ExecutionError: If code execution fails
            TimeoutError: If execution times out

        Example:
            >>> # Isolated mode (default)
            >>> result = session.run("a = 2")
            >>> result = session.run("print(a)")  # Error: a not defined

            >>> # Persistent mode
            >>> session.start()
            >>> session.run("a = 2")
            >>> session.run("print(a)")  # prints: 2
            >>> session.stop()
        """
        timeout = timeout or self.timeout

        # If persistent session is active, use persistent exec
        if self._persistent_id:
            return self._run_persistent(code, timeout, stream)

        # Otherwise use normal execution
        if stream:
            return self._run_streaming(code, timeout)
        else:
            return self._run_sync(code, timeout)

    def _run_persistent(self, code: str, timeout: int, stream: bool) -> ExecutionResult:
        """Execute code in persistent session."""
        response = requests.post(
            f"{self.base_url}/api/session/exec/",
            headers=self._headers(),
            json={
                "persistent_id": self._persistent_id,
                "code": code,
                "timeout": timeout
            },
            timeout=timeout + 10
        )

        data = self._check_response(response)

        output = data.get("output", "")
        if stream and output and output != "(Aucune sortie)":
            print(output)

        return ExecutionResult(
            output=output,
            result=data.get("result"),  # Résultat d'expression pour get()
            error="" if data.get("success") else data.get("error", ""),
            exit_code=0 if data.get("success") else 1,
            success=data.get("success", False)
        )

    def _run_sync(self, code: str, timeout: int) -> ExecutionResult:
        """Execute code synchronously without streaming."""
        response = requests.post(
            f"{self.base_url}/api/execute/",
            headers=self._headers(),
            json={"code": code},
            timeout=timeout + 10
        )

        data = self._check_response(response)

        return ExecutionResult(
            output=data.get("output", ""),
            result=data.get("result"),
            error=data.get("error", ""),
            exit_code=int(data.get("exit_code", 0)),
            success=data.get("success", True)
        )

    def _run_streaming(self, code: str, timeout: int) -> ExecutionResult:
        """Execute code with real-time streaming output."""
        import sys

        try:
            response = requests.post(
                f"{self.base_url}/api/stream/",
                headers=self._headers(),
                json={"code": code, "timeout": timeout},
                stream=True,
                timeout=None  # No timeout for streaming
            )

            if response.status_code != 200:
                # Fall back to sync mode if streaming not available
                return self._run_sync(code, timeout)

            output_lines = []
            exit_code = 0
            success = True

            # Parse Server-Sent Events
            for line in response.iter_lines(decode_unicode=True):
                if not line:
                    continue

                if line.startswith("event:"):
                    event_type = line[6:].strip()
                elif line.startswith("data:"):
                    data_str = line[5:].strip()
                    try:
                        data = json.loads(data_str)

                        if event_type == "output":
                            line_text = data.get("line", "")
                            stream_type = data.get("stream", "stdout")
                            output_lines.append(line_text)

                            # Print to appropriate stream
                            if stream_type == "stderr":
                                print(line_text, file=sys.stderr)
                            else:
                                print(line_text)

                        elif event_type == "done":
                            success = data.get("success", True)
                            exit_code = data.get("exit_code", 0)
                            break

                        elif event_type == "error":
                            error_msg = data.get("error", "Unknown error")
                            raise ExecutionError(error_msg)

                    except json.JSONDecodeError:
                        pass

            return ExecutionResult(
                output="\n".join(output_lines),
                result=None,
                error="" if success else "Execution failed",
                exit_code=exit_code,
                success=success
            )

        except requests.exceptions.RequestException as e:
            # Fall back to sync mode on connection error
            return self._run_sync(code, timeout)

    def exec(self, code: str, timeout: Optional[int] = None) -> bool:
        """
        Execute Python code without returning a result.

        Similar to run() but optimized for code that doesn't need a return value.
        Raises an exception if execution fails.

        Args:
            code: Python code to execute
            timeout: Timeout in seconds

        Returns:
            True if execution succeeded.

        Raises:
            ExecutionError: If code execution fails

        Example:
            >>> session.exec("import torch")
            >>> session.exec("model = load_model()")
        """
        result = self.run(code, timeout)
        if not result.success:
            raise ExecutionError(result.error)
        return True

    def shell(self, command: str, timeout: Optional[int] = None) -> ExecutionResult:
        """
        Execute a shell command on the remote GPU pod.

        Args:
            command: Shell command to execute
            timeout: Timeout in seconds

        Returns:
            ExecutionResult with command output.

        Raises:
            CommandBlockedError: If command is blocked by security filters
            ExecutionError: If command fails

        Example:
            >>> # List files
            >>> result = session.shell("ls -la /workspace")
            >>> print(result.output)

            >>> # Check disk space
            >>> result = session.shell("df -h")

            >>> # Multiple commands
            >>> result = session.shell("cd /workspace && ls && pwd")
        """
        timeout = timeout or self.timeout

        response = requests.post(
            f"{self.base_url}/api/shell/",
            headers=self._headers(),
            json={"command": command},
            timeout=timeout + 10
        )

        data = self._check_response(response)

        return ExecutionResult(
            output=data.get("output", ""),
            result=None,
            error=data.get("error", ""),
            exit_code=int(data.get("exit_code", 0)),
            success=data.get("success", True)
        )

    def set(self, name: str, value: Any) -> bool:
        """
        Send a local variable to the remote GPU session.

        The variable is serialized with pickle and stored in the Python
        environment on the remote GPU pod.

        Args:
            name: Variable name on the remote session
            value: Value to send (must be picklable)

        Returns:
            True if successful.

        Raises:
            ClouditiaError: If value cannot be serialized

        Example:
            >>> # Send data to GPU
            >>> session.set("data", [1, 2, 3, 4, 5])
            >>> session.run("print(sum(data))")  # prints: 15

            >>> # Send numpy arrays
            >>> import numpy as np
            >>> session.set("arr", np.random.randn(100, 100))
        """
        try:
            pickled = pickle.dumps(value)
            value_b64 = base64.b64encode(pickled).decode()
        except Exception as e:
            raise ClouditiaError(f"Cannot serialize value: {e}")

        code = f'''
import pickle
import base64
{name} = pickle.loads(base64.b64decode("{value_b64}"))
globals()["{name}"] = {name}
'''
        result = self.run(code)
        if not result.success:
            raise ExecutionError(f"Failed to set variable: {result.error}")

        self._remote_vars[name] = True
        return True

    def get(self, name: str) -> Any:
        """
        Retrieve a variable from the remote GPU session.

        The variable is serialized on the remote pod and deserialized locally.

        Args:
            name: Variable name to retrieve

        Returns:
            The value of the variable.

        Raises:
            ExecutionError: If variable doesn't exist or can't be retrieved

        Example:
            >>> session.run("result = [i**2 for i in range(10)]")
            >>> data = session.get("result")
            >>> print(data)  # [0, 1, 4, 9, 16, 25, 36, 49, 64, 81]
        """
        code = f'''
import pickle
import base64
_tmp_value = base64.b64encode(pickle.dumps({name})).decode()
_tmp_value
'''
        result = self.run(code)

        if not result.success:
            raise ExecutionError(f"Failed to get variable: {result.error}")

        if result.result is None:
            raise ExecutionError(f"Variable '{name}' not found or not serializable")

        try:
            value_b64 = result.result.strip().strip("'\"")
            pickled = base64.b64decode(value_b64)
            return pickle.loads(pickled)
        except Exception as e:
            raise ClouditiaError(f"Cannot deserialize value: {e}")

    # ==================== FILE TRANSFER METHODS ====================

    def upload(
        self,
        local_path: Union[str, Path],
        remote_path: str,
        show_progress: bool = True
    ) -> bool:
        """
        Upload a file from local machine to the remote GPU session.

        Args:
            local_path: Path to the local file
            remote_path: Destination path on the remote pod
            show_progress: Show upload progress (default: True)

        Returns:
            True if upload succeeded.

        Raises:
            FileNotFoundError: If local file doesn't exist
            ClouditiaError: If upload fails

        Example:
            >>> session.upload("./data.csv", "/workspace/data.csv")
            >>> session.upload("model.pkl", "/workspace/models/model.pkl")
        """
        local_path = Path(local_path)

        if not local_path.exists():
            raise FileNotFoundError(f"Local file not found: {local_path}")

        if not local_path.is_file():
            raise ClouditiaError(f"Not a file: {local_path}. Use upload_folder() for directories.")

        # Read and encode file
        file_size = local_path.stat().st_size
        if show_progress:
            print(f"📤 Uploading {local_path.name} ({self._format_size(file_size)})...")

        with open(local_path, 'rb') as f:
            file_data = f.read()

        file_b64 = base64.b64encode(file_data).decode()

        # Create directory and write file on remote
        remote_dir = os.path.dirname(remote_path)
        code = f'''
import base64
import os

# Create directory if needed
os.makedirs("{remote_dir}", exist_ok=True)

# Decode and write file
file_data = base64.b64decode("{file_b64}")
with open("{remote_path}", "wb") as f:
    f.write(file_data)

print(f"File written: {remote_path} ({{len(file_data)}} bytes)")
'''
        result = self.run(code, stream=False)

        if not result.success:
            raise ClouditiaError(f"Upload failed: {result.error}")

        if show_progress:
            print(f"✅ Uploaded to {remote_path}")

        return True

    def download(
        self,
        remote_path: str,
        local_path: Union[str, Path],
        show_progress: bool = True
    ) -> bool:
        """
        Download a file from the remote GPU session to local machine.

        Args:
            remote_path: Path to the file on the remote pod
            local_path: Destination path on local machine
            show_progress: Show download progress (default: True)

        Returns:
            True if download succeeded.

        Raises:
            ClouditiaError: If file doesn't exist or download fails

        Example:
            >>> session.download("/workspace/results.csv", "./results.csv")
            >>> session.download("/workspace/model.pt", "./models/trained_model.pt")
        """
        local_path = Path(local_path)

        if show_progress:
            print(f"📥 Downloading {os.path.basename(remote_path)}...")

        # Read and encode file on remote - use print to output the base64
        code = f'''
import base64
import os

if not os.path.exists("{remote_path}"):
    raise FileNotFoundError("File not found: {remote_path}")

if os.path.isdir("{remote_path}"):
    raise IsADirectoryError("Path is a directory. Use download_folder() instead.")

with open("{remote_path}", "rb") as f:
    file_data = f.read()

file_b64 = base64.b64encode(file_data).decode()
print("__FILEDATA_START__")
print(file_b64)
print("__FILEDATA_END__")
'''
        result = self.run(code, stream=False)

        if not result.success:
            raise ClouditiaError(f"Download failed: {result.error}")

        # Extract base64 data from output
        output = result.output or ""
        if "__FILEDATA_START__" not in output or "__FILEDATA_END__" not in output:
            raise ClouditiaError("No data received from remote")

        # Parse the base64 data between markers
        try:
            start = output.index("__FILEDATA_START__") + len("__FILEDATA_START__")
            end = output.index("__FILEDATA_END__")
            file_b64 = output[start:end].strip()
            file_data = base64.b64decode(file_b64)
        except Exception as e:
            raise ClouditiaError(f"Failed to decode file data: {e}")

        # Create local directory if needed
        local_path.parent.mkdir(parents=True, exist_ok=True)

        with open(local_path, 'wb') as f:
            f.write(file_data)

        if show_progress:
            print(f"✅ Downloaded to {local_path} ({self._format_size(len(file_data))})")

        return True

    def upload_folder(
        self,
        local_path: Union[str, Path],
        remote_path: str,
        exclude: Optional[List[str]] = None,
        show_progress: bool = True
    ) -> bool:
        """
        Upload an entire folder from local machine to the remote GPU session.

        The folder is compressed locally, transferred, and extracted on the remote.

        Args:
            local_path: Path to the local folder
            remote_path: Destination path on the remote pod
            exclude: List of patterns to exclude (e.g., ['__pycache__', '.git', '*.pyc'])
            show_progress: Show upload progress (default: True)

        Returns:
            True if upload succeeded.

        Raises:
            FileNotFoundError: If local folder doesn't exist
            ClouditiaError: If upload fails

        Example:
            >>> session.upload_folder("./my_project", "/workspace/project")
            >>> session.upload_folder("./data", "/workspace/data", exclude=['*.tmp', '.git'])
        """
        local_path = Path(local_path)

        if not local_path.exists():
            raise FileNotFoundError(f"Local folder not found: {local_path}")

        if not local_path.is_dir():
            raise ClouditiaError(f"Not a directory: {local_path}. Use upload() for files.")

        # Default exclusions
        if exclude is None:
            exclude = ['__pycache__', '.git', '*.pyc', '.DS_Store', 'node_modules']

        if show_progress:
            print(f"📦 Compressing {local_path.name}...")

        # Create tar.gz in memory
        tar_buffer = io.BytesIO()

        def filter_func(tarinfo):
            # Check exclusion patterns
            for pattern in exclude:
                if pattern.startswith('*'):
                    if tarinfo.name.endswith(pattern[1:]):
                        return None
                elif pattern in tarinfo.name:
                    return None
            return tarinfo

        with tarfile.open(fileobj=tar_buffer, mode='w:gz') as tar:
            tar.add(local_path, arcname=os.path.basename(local_path), filter=filter_func)

        tar_data = tar_buffer.getvalue()
        tar_b64 = base64.b64encode(tar_data).decode()

        if show_progress:
            print(f"📤 Uploading {self._format_size(len(tar_data))}...")

        # Transfer and extract on remote
        code = f'''
import base64
import tarfile
import io
import os

# Decode tar data
tar_data = base64.b64decode("{tar_b64}")

# Create destination directory
os.makedirs("{remote_path}", exist_ok=True)

# Extract
tar_buffer = io.BytesIO(tar_data)
with tarfile.open(fileobj=tar_buffer, mode='r:gz') as tar:
    tar.extractall(path="{remote_path}")

# Count files
file_count = sum(1 for root, dirs, files in os.walk("{remote_path}") for f in files)
print(f"Extracted {{file_count}} files to {remote_path}")
'''
        result = self.run(code, stream=False)

        if not result.success:
            raise ClouditiaError(f"Upload folder failed: {result.error}")

        if show_progress:
            print(f"✅ Folder uploaded to {remote_path}")

        return True

    def download_folder(
        self,
        remote_path: str,
        local_path: Union[str, Path],
        exclude: Optional[List[str]] = None,
        show_progress: bool = True
    ) -> bool:
        """
        Download an entire folder from the remote GPU session to local machine.

        The folder is compressed on the remote, transferred, and extracted locally.

        Args:
            remote_path: Path to the folder on the remote pod
            local_path: Destination path on local machine
            exclude: List of patterns to exclude (e.g., ['__pycache__', '*.pyc'])
            show_progress: Show download progress (default: True)

        Returns:
            True if download succeeded.

        Raises:
            ClouditiaError: If folder doesn't exist or download fails

        Example:
            >>> session.download_folder("/workspace/results", "./results")
            >>> session.download_folder("/workspace/checkpoints", "./checkpoints", exclude=['*.tmp'])
        """
        local_path = Path(local_path)

        # Default exclusions
        if exclude is None:
            exclude = ['__pycache__', '*.pyc', '.DS_Store']

        if show_progress:
            print(f"📦 Compressing remote folder...")

        # Build exclude filter for Python
        exclude_patterns = repr(exclude)

        # Compress on remote and get base64
        code = f'''
import base64
import tarfile
import io
import os
import fnmatch

if not os.path.exists("{remote_path}"):
    raise FileNotFoundError("Folder not found: {remote_path}")

if not os.path.isdir("{remote_path}"):
    raise NotADirectoryError("Path is not a directory. Use download() instead.")

exclude_patterns = {exclude_patterns}

def should_exclude(name):
    for pattern in exclude_patterns:
        if fnmatch.fnmatch(name, pattern) or fnmatch.fnmatch(os.path.basename(name), pattern):
            return True
    return False

def filter_func(tarinfo):
    if should_exclude(tarinfo.name):
        return None
    return tarinfo

# Create tar.gz in memory
tar_buffer = io.BytesIO()
with tarfile.open(fileobj=tar_buffer, mode='w:gz') as tar:
    tar.add("{remote_path}", arcname=os.path.basename("{remote_path}"), filter=filter_func)

tar_data = tar_buffer.getvalue()
tar_b64 = base64.b64encode(tar_data).decode()
print(f"Compressed size: {{len(tar_data)}} bytes")
print("__FOLDERDATA_START__")
print(tar_b64)
print("__FOLDERDATA_END__")
'''
        result = self.run(code, stream=False)

        if not result.success:
            raise ClouditiaError(f"Download folder failed: {result.error}")

        # Extract base64 data from output
        output = result.output or ""
        if "__FOLDERDATA_START__" not in output or "__FOLDERDATA_END__" not in output:
            raise ClouditiaError("No data received from remote")

        if show_progress:
            print(f"📥 Downloading...")

        # Decode and extract locally
        try:
            start = output.index("__FOLDERDATA_START__") + len("__FOLDERDATA_START__")
            end = output.index("__FOLDERDATA_END__")
            tar_b64 = output[start:end].strip()
            tar_data = base64.b64decode(tar_b64)
        except Exception as e:
            raise ClouditiaError(f"Failed to decode folder data: {e}")

        # Create local directory
        local_path.mkdir(parents=True, exist_ok=True)

        # Extract
        tar_buffer = io.BytesIO(tar_data)
        with tarfile.open(fileobj=tar_buffer, mode='r:gz') as tar:
            tar.extractall(path=local_path)

        # Count files
        file_count = sum(1 for root, dirs, files in os.walk(local_path) for f in files)

        if show_progress:
            print(f"✅ Downloaded to {local_path} ({file_count} files, {self._format_size(len(tar_data))})")

        return True

    def list_files(
        self,
        remote_path: str = "/workspace",
        pattern: Optional[str] = None
    ) -> List[Dict]:
        """
        List files in a remote directory.

        Args:
            remote_path: Directory path to list (default: /workspace)
            pattern: Optional glob pattern to filter files (e.g., '*.py')

        Returns:
            List of dicts with file info (name, path, size, is_dir, modified).

        Example:
            >>> files = session.list_files("/workspace")
            >>> for f in files:
            ...     print(f"{f['name']} - {f['size']} bytes")

            >>> py_files = session.list_files("/workspace", pattern="*.py")
        """
        pattern_code = f'"{pattern}"' if pattern else 'None'

        code = f'''
import os
import json
from datetime import datetime
import fnmatch

path = "{remote_path}"
pattern = {pattern_code}

if not os.path.exists(path):
    raise FileNotFoundError(f"Path not found: {{path}}")

files = []
for item in os.listdir(path):
    item_path = os.path.join(path, item)
    stat = os.stat(item_path)

    if pattern and not fnmatch.fnmatch(item, pattern):
        continue

    files.append({{
        "name": item,
        "path": item_path,
        "size": stat.st_size,
        "is_dir": os.path.isdir(item_path),
        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
    }})

# Sort: directories first, then by name
files.sort(key=lambda x: (not x["is_dir"], x["name"].lower()))

print("__LISTFILES_START__")
print(json.dumps(files))
print("__LISTFILES_END__")
'''
        result = self.run(code, stream=False)

        if not result.success:
            raise ClouditiaError(f"Failed to list files: {result.error}")

        output = result.output or ""
        if "__LISTFILES_START__" in output and "__LISTFILES_END__" in output:
            try:
                start = output.index("__LISTFILES_START__") + len("__LISTFILES_START__")
                end = output.index("__LISTFILES_END__")
                files_json = output[start:end].strip()
                return json.loads(files_json)
            except (json.JSONDecodeError, ValueError):
                return []

        return []

    def file_exists(self, remote_path: str) -> bool:
        """
        Check if a file or directory exists on the remote pod.

        Args:
            remote_path: Path to check

        Returns:
            True if path exists, False otherwise.

        Example:
            >>> if session.file_exists("/workspace/model.pt"):
            ...     session.download("/workspace/model.pt", "./model.pt")
        """
        code = f'''
import os
exists = os.path.exists("{remote_path}")
print("__EXISTS_START__")
print("TRUE" if exists else "FALSE")
print("__EXISTS_END__")
'''
        result = self.run(code, stream=False)

        output = result.output or ""
        if "__EXISTS_START__" in output and "__EXISTS_END__" in output:
            start = output.index("__EXISTS_START__") + len("__EXISTS_START__")
            end = output.index("__EXISTS_END__")
            value = output[start:end].strip()
            return value == "TRUE"
        return False

    def _format_size(self, size: int) -> str:
        """Format file size in human-readable format."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"

    # ==================== END FILE TRANSFER METHODS ====================

    def submit(
        self,
        code: str,
        name: Optional[str] = None,
        job_type: str = "python"
    ) -> AsyncJob:
        """
        Submit a long-running job for asynchronous execution.

        Use this for tasks that take hours or days (like model training).
        The job runs in the background and you can monitor its progress.

        Args:
            code: Python code or shell command to execute
            name: Optional name to identify the job
            job_type: "python" or "shell"

        Returns:
            AsyncJob instance for monitoring and control.

        Example:
            >>> job = session.submit('''
            ... for epoch in range(100):
            ...     print(f"Epoch {epoch}/100")
            ...     train_one_epoch()
            ... save_model()
            ... ''', name="model_training")
            >>>
            >>> print(f"Job ID: {job.job_id}")
            >>>
            >>> # Wait with live logs
            >>> result = job.wait(show_logs=True)

            >>> # Or poll manually
            >>> while not job.is_done():
            ...     print(job.logs(new_only=True))
            ...     time.sleep(30)
        """
        response = requests.post(
            f"{self.base_url}/api/jobs/submit/",
            headers=self._headers(),
            json={
                "code": code,
                "name": name or "",
                "type": job_type
            },
            timeout=30
        )

        data = self._check_response(response)

        return AsyncJob(
            session=self,
            job_id=data["job_id"],
            name=name
        )

    def jobs(
        self,
        status: Optional[str] = None,
        limit: int = 10
    ) -> List[AsyncJob]:
        """
        List async jobs for this session.

        Args:
            status: Filter by status (pending, running, completed, failed, cancelled)
            limit: Maximum number of jobs to return

        Returns:
            List of AsyncJob instances.

        Example:
            >>> # List all running jobs
            >>> running = session.jobs(status="running")
            >>> for job in running:
            ...     print(f"{job.name}: {job.status()}")

            >>> # List recent completed jobs
            >>> completed = session.jobs(status="completed", limit=5)
        """
        params = {"limit": limit}
        if status:
            params["status"] = status

        response = requests.get(
            f"{self.base_url}/api/jobs/list/",
            headers=self._headers(),
            params=params,
            timeout=30
        )

        data = self._check_response(response)

        return [
            AsyncJob(
                session=self,
                job_id=job["job_id"],
                name=job.get("name"),
                _data=job
            )
            for job in data.get("jobs", [])
        ]

    def remote(
        self,
        func: Optional[Callable] = None,
        **kwargs
    ) -> Callable:
        """
        Decorator to execute a function on the remote GPU.

        The function is serialized, sent to the GPU, executed, and the
        result is returned locally. All arguments must be picklable.

        Args:
            func: Function to decorate
            **kwargs: Options (async_mode, timeout)

        Returns:
            Decorated function that runs on remote GPU.

        Example:
            >>> @session.remote
            ... def compute_on_gpu(data):
            ...     import torch
            ...     tensor = torch.tensor(data, device='cuda')
            ...     return (tensor ** 2).sum().item()
            >>>
            >>> result = compute_on_gpu([1, 2, 3, 4, 5])
            >>> print(result)  # 55

            >>> # Async mode
            >>> @session.remote(async_mode=True)
            ... def train():
            ...     # long training code
            ...     pass
            >>>
            >>> job = train()  # Returns AsyncJob
        """
        async_mode = kwargs.get("async_mode", False)
        timeout = kwargs.get("timeout", self.timeout)

        def decorator(fn: Callable) -> Callable:
            @wraps(fn)
            def wrapper(*args, **kw):
                # Get function source
                source = inspect.getsource(fn)
                source = textwrap.dedent(source)

                # Remove decorator from source
                lines = source.split("\n")
                func_start = 0
                for i, line in enumerate(lines):
                    if line.strip().startswith("def "):
                        func_start = i
                        break
                source = "\n".join(lines[func_start:])

                # Serialize arguments
                args_b64 = base64.b64encode(pickle.dumps(args)).decode()
                kwargs_b64 = base64.b64encode(pickle.dumps(kw)).decode()

                exec_code = f'''
import pickle
import base64

# Define the function
{source}

# Deserialize arguments
_args = pickle.loads(base64.b64decode("{args_b64}"))
_kwargs = pickle.loads(base64.b64decode("{kwargs_b64}"))

# Execute function
_result = {fn.__name__}(*_args, **_kwargs)

# Serialize result
_result_b64 = base64.b64encode(pickle.dumps(_result)).decode()
_result_b64
'''

                if async_mode:
                    return self.submit(exec_code, name=fn.__name__)
                else:
                    result = self.run(exec_code, timeout=timeout)

                    if not result.success:
                        raise ExecutionError(f"Remote execution failed: {result.error}")

                    if result.result:
                        try:
                            value_b64 = result.result.strip().strip("'\"")
                            pickled = base64.b64decode(value_b64)
                            return pickle.loads(pickled)
                        except Exception as e:
                            raise ClouditiaError(f"Cannot deserialize result: {e}")

                    return None

            return wrapper

        if func is not None:
            return decorator(func)
        return decorator

    def gpu_info(self) -> Dict:
        """
        Get detailed GPU information from the remote pod.

        Returns:
            Dict with GPU details (name, memory, utilization).

        Example:
            >>> info = session.gpu_info()
            >>> for gpu in info['gpus']:
            ...     print(f"{gpu['name']}: {gpu['memory_used_mb']}/{gpu['memory_total_mb']} MB")
        """
        # Use a safe command to get GPU info
        result = self.run('''
import subprocess
result = subprocess.run(
    ["nvidia-smi", "--query-gpu=name,memory.total,memory.used,memory.free,utilization.gpu",
     "--format=csv,noheader,nounits"],
    capture_output=True, text=True
)
print(result.stdout)
''')

        if not result.success:
            raise ExecutionError("Failed to get GPU info")

        lines = result.output.strip().split("\n")
        gpus = []

        for line in lines:
            parts = [p.strip() for p in line.split(",")]
            if len(parts) >= 5:
                gpus.append({
                    "name": parts[0],
                    "memory_total_mb": int(parts[1]),
                    "memory_used_mb": int(parts[2]),
                    "memory_free_mb": int(parts[3]),
                    "utilization_percent": int(parts[4])
                })

        return {"gpus": gpus, "count": len(gpus)}

    @property
    def session_info(self) -> Optional[Dict]:
        """
        Get cached session information.

        Call verify() first to populate this property.

        Returns:
            Session info dict or None if not yet verified.
        """
        return self._session_info

    def __repr__(self) -> str:
        """Return string representation."""
        key_preview = self.api_key[:10] + "..." if len(self.api_key) > 10 else self.api_key
        return f"GPUSession(api_key='{key_preview}')"

    def __str__(self) -> str:
        """Return human-readable string."""
        if self._session_info:
            return f"GPUSession({self._session_info.get('session_name', 'connected')})"
        return f"GPUSession(not verified)"


def connect(api_key: str, **kwargs) -> GPUSession:
    """
    Create and return a GPU session.

    This is a convenience function equivalent to GPUSession(api_key).

    Args:
        api_key: Your Clouditia API key
        **kwargs: Additional options for GPUSession

    Returns:
        Configured GPUSession instance.

    Example:
        >>> from clouditia import connect
        >>> session = connect("ck_your_api_key")
        >>> result = session.run("print('Hello!')")
    """
    return GPUSession(api_key, **kwargs)

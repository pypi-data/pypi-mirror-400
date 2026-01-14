# Clouditia SDK

**Execute Python and Shell code on remote GPU sessions.**

Clouditia SDK provides a simple Python interface to run code on remote GPU-powered containers. Perfect for machine learning, deep learning, and any GPU-accelerated workloads.

[![PyPI version](https://badge.fury.io/py/clouditia.svg)](https://pypi.org/project/clouditia/)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Installation

```bash
pip install clouditia
```

## Quick Start

```python
from clouditia import GPUSession

# Connect to your GPU session
session = GPUSession("ck_your_api_key")

# Execute Python code on the remote GPU
result = session.run("""
import torch
print(f"CUDA available: {torch.cuda.is_available()}")
print(f"GPU: {torch.cuda.get_device_name(0)}")
""")

print(result.output)
```

## Features

- **Python Execution**: Run Python code on remote GPUs
- **Shell Commands**: Execute shell commands on the GPU pod
- **Persistent Sessions**: Keep variables between executions with `start()`/`stop()`
- **Variable Transfer**: Send and retrieve variables between local and remote
- **File Transfer**: Upload/download files and folders between local and remote
- **Async Jobs**: Submit long-running tasks with real-time log monitoring
- **Jupyter Magic**: Use `%%clouditia` magic in notebooks
- **Decorator Support**: Use `@session.remote` to run functions on GPU

---

## Table of Contents

1. [Getting Your API Key](#getting-your-api-key)
2. [Basic Usage](#basic-usage)
3. [Persistent Sessions](#persistent-sessions)
4. [Executing Python Code](#executing-python-code)
5. [Shell Commands](#shell-commands)
6. [Variable Transfer](#variable-transfer)
7. [File Transfer](#file-transfer)
8. [Remote Functions (Decorator)](#remote-functions-decorator)
9. [Async Jobs (Long-Running Tasks)](#async-jobs-long-running-tasks)
10. [Jupyter Magic](#jupyter-magic)
11. [Error Handling](#error-handling)
12. [API Reference](#api-reference)

---

## Getting Your API Key

1. Log in to [clouditia.com](https://clouditia.com)
2. Start a GPU session
3. Go to **API Keys** in your session dashboard
4. Generate a new API key (starts with `ck_` or `sk_`)

---

## Basic Usage

### Connect to a Session

```python
from clouditia import GPUSession

# Create a session with your API key
session = GPUSession("ck_your_api_key_here")

# Verify the connection
info = session.verify()
print(f"Connected to: {info['session_name']}")
print(f"GPU: {info['gpu_type']}")
print(f"Credit remaining: {info['user_credit']}€")
```

### Using the `connect()` Function

```python
from clouditia import connect

session = connect("ck_your_api_key")
result = session.run("print('Hello from GPU!')")
```

---

## Persistent Sessions

By default, each `run()` call executes in an isolated environment - variables don't persist between calls. Use `start()` and `stop()` to enable persistent sessions where variables are preserved.

### Isolated Mode (Default)

```python
# Without start(), variables are NOT persistent
session.run("x = 10")
session.run("print(x)")  # Error: x is not defined
```

### Persistent Mode

```python
# Start a persistent session
session.start()
print(f"Session active: {session.is_persistent}")  # True

# Variables now persist between run() calls
session.run("x = 10")
session.run("y = 20")
session.run("z = x + y")
result = session.run("print(f'Result: {z}')")
# Output: Result: 30

# Stop the session when done
session.stop()
print(f"Session active: {session.is_persistent}")  # False
```

### Full Example

```python
from clouditia import GPUSession

session = GPUSession("ck_your_api_key")

# Start persistent session
session.start()

# Build up state across multiple calls
session.run("import torch")
session.run("model = torch.nn.Linear(10, 5).cuda()")
session.run("data = torch.randn(32, 10).cuda()")

# Use the accumulated state
result = session.run("""
output = model(data)
print(f"Input shape: {data.shape}")
print(f"Output shape: {output.shape}")
""")

# Clean up
session.stop()
```

### Checking Session State

```python
# Check if a persistent session is active
if session.is_persistent:
    print("Persistent session is running")
else:
    print("Running in isolated mode")
```

---

## Executing Python Code

### Simple Execution

```python
# Run Python code and get the output
result = session.run("print('Hello from the GPU!')")
print(result.output)  # "Hello from the GPU!"

# Check if execution was successful
if result.success:
    print("Code executed successfully!")
else:
    print(f"Error: {result.error}")
```

### Getting Return Values

```python
# The last expression is captured as result
result = session.run("2 + 2")
print(result.result)  # "4"

result = session.run("[i**2 for i in range(5)]")
print(result.result)  # "[0, 1, 4, 9, 16]"
```

### Multi-line Code

```python
result = session.run("""
import torch
import torch.nn as nn

# Create a simple model
model = nn.Linear(10, 5).cuda()
x = torch.randn(32, 10).cuda()
output = model(x)

print(f"Input shape: {x.shape}")
print(f"Output shape: {output.shape}")
print(f"Model parameters: {sum(p.numel() for p in model.parameters())}")
""")

print(result.output)
```

### Using exec() for Side Effects

```python
# exec() is for code that doesn't need a return value
session.exec("import torch")
session.exec("model = torch.nn.Linear(10, 5).cuda()")
session.exec("optimizer = torch.optim.Adam(model.parameters())")
```

---

## Shell Commands

Execute shell commands on the remote GPU pod:

```python
# List files
result = session.shell("ls -la /workspace")
print(result.output)

# Check current directory
result = session.shell("pwd")
print(result.output)

# Create directories and files
result = session.shell("mkdir -p /workspace/models && ls /workspace")
print(result.output)

# Chain multiple commands
result = session.shell("cd /workspace && mkdir data && ls -la")
print(result.output)

# Check disk space
result = session.shell("df -h")
print(result.output)

# Check memory
result = session.shell("free -h")
print(result.output)

# Install packages
result = session.shell("pip install transformers datasets")
print(result.output)

# Download files
result = session.shell("wget https://example.com/data.zip -O /workspace/data.zip")
print(result.output)
```

### Checking Exit Codes

```python
result = session.shell("ls /nonexistent")
print(f"Exit code: {result.exit_code}")
print(f"Success: {result.success}")
```

---

## Variable Transfer

### Sending Variables to GPU

```python
# Send local data to the remote session
data = [1, 2, 3, 4, 5]
session.set("my_data", data)

# Use it in remote code
session.run("print(f'Data: {my_data}')")
session.run("print(f'Sum: {sum(my_data)}')")
```

### Retrieving Variables from GPU

```python
# Compute something on the GPU
session.run("""
import torch
tensor = torch.randn(100, 100).cuda()
result_stats = {
    'mean': tensor.mean().item(),
    'std': tensor.std().item(),
    'shape': list(tensor.shape)
}
""")

# Get the result locally
stats = session.get("result_stats")
print(f"Mean: {stats['mean']:.4f}")
print(f"Std: {stats['std']:.4f}")
print(f"Shape: {stats['shape']}")
```

### Sending Complex Objects

```python
import numpy as np

# Send numpy arrays
arr = np.random.randn(100, 100)
session.set("numpy_array", arr)

# Send dictionaries
config = {
    "learning_rate": 0.001,
    "batch_size": 32,
    "epochs": 100
}
session.set("config", config)

# Use in remote code
session.run("""
import torch
tensor = torch.from_numpy(numpy_array).cuda()
print(f"Learning rate: {config['learning_rate']}")
""")
```

---

## File Transfer

Transfer files and folders between your local machine and the remote GPU session.

### Uploading a Single File

```python
# Upload a local file to the remote session
session.upload("./data.csv", "/home/coder/workspace/data.csv")

# Upload with custom path
session.upload("./model.pkl", "/home/coder/workspace/models/trained_model.pkl")

# Disable progress output
session.upload("./config.json", "/home/coder/workspace/config.json", show_progress=False)
```

### Downloading a Single File

```python
# Download a file from the remote session
session.download("/home/coder/workspace/results.csv", "./results.csv")

# Download trained model
session.download("/home/coder/workspace/checkpoints/model.pt", "./local_model.pt")

# Download silently
session.download("/home/coder/workspace/logs.txt", "./logs.txt", show_progress=False)
```

### Uploading a Folder

Upload an entire directory with all its contents:

```python
# Upload a project folder
session.upload_folder("./my_project", "/home/coder/workspace/project")

# Upload with exclusions (default excludes: __pycache__, .git, *.pyc, .DS_Store, node_modules)
session.upload_folder(
    "./my_project",
    "/home/coder/workspace/project",
    exclude=["*.log", ".env", "__pycache__", ".git"]
)

# Upload data folder
session.upload_folder("./datasets", "/home/coder/workspace/data")
```

### Downloading a Folder

Download an entire directory with all its contents:

```python
# Download results folder
session.download_folder("/home/coder/workspace/results", "./local_results")

# Download checkpoints
session.download_folder(
    "/home/coder/workspace/checkpoints",
    "./checkpoints",
    exclude=["*.tmp", "*.log"]
)

# Download trained models
session.download_folder("/home/coder/workspace/models", "./downloaded_models")
```

### Listing Remote Files

```python
# List files in a directory
files = session.list_files("/home/coder/workspace")
for f in files:
    icon = "📁" if f["is_dir"] else "📄"
    print(f"{icon} {f['name']} - {f['size']} bytes")

# Filter by pattern
python_files = session.list_files("/home/coder/workspace", pattern="*.py")
for f in python_files:
    print(f"📄 {f['name']}")

# List with full details
files = session.list_files("/home/coder/workspace")
for f in files:
    print(f"Name: {f['name']}")
    print(f"  Path: {f['path']}")
    print(f"  Size: {f['size']} bytes")
    print(f"  Is Directory: {f['is_dir']}")
    print(f"  Modified: {f['modified']}")
```

### Checking if a File Exists

```python
# Check before downloading
if session.file_exists("/home/coder/workspace/model.pt"):
    session.download("/home/coder/workspace/model.pt", "./model.pt")
    print("Model downloaded!")
else:
    print("Model not found, training required...")

# Check multiple files
files_to_check = ["config.json", "data.csv", "model.pt"]
for filename in files_to_check:
    path = f"/home/coder/workspace/{filename}"
    exists = session.file_exists(path)
    status = "✓" if exists else "✗"
    print(f"{status} {filename}")
```

### Complete Workflow Example

```python
from clouditia import GPUSession

session = GPUSession("ck_your_api_key")

# 1. Upload training data and code
session.upload_folder("./training_code", "/home/coder/workspace/code")
session.upload("./data/train.csv", "/home/coder/workspace/data/train.csv")
session.upload("./data/test.csv", "/home/coder/workspace/data/test.csv")

# 2. Run training
result = session.run("""
import sys
sys.path.insert(0, '/home/coder/workspace/code')
from train import train_model

model = train_model('/home/coder/workspace/data/train.csv')
model.save('/home/coder/workspace/output/model.pt')
print("Training complete!")
""")

# 3. Check and download results
if session.file_exists("/home/coder/workspace/output/model.pt"):
    session.download("/home/coder/workspace/output/model.pt", "./trained_model.pt")
    print("Model saved locally!")

# 4. Download all outputs
session.download_folder("/home/coder/workspace/output", "./results")
print("All results downloaded!")

# 5. List what was created
files = session.list_files("/home/coder/workspace/output")
print(f"Created {len(files)} files during training")
```

### Working with Different File Types

```python
# CSV files
session.upload("./data.csv", "/home/coder/workspace/data.csv")

# Pickle files (models, data)
session.upload("./model.pkl", "/home/coder/workspace/model.pkl")

# PyTorch models
session.download("/home/coder/workspace/checkpoint.pt", "./checkpoint.pt")

# JSON configuration
session.upload("./config.json", "/home/coder/workspace/config.json")

# Text files
session.upload("./requirements.txt", "/home/coder/workspace/requirements.txt")

# Binary files
session.upload("./image.png", "/home/coder/workspace/image.png")

# Any file type works!
session.upload("./data.parquet", "/home/coder/workspace/data.parquet")
session.upload("./weights.h5", "/home/coder/workspace/weights.h5")
```

---

## Remote Functions (Decorator)

Use the `@session.remote` decorator to run functions on the GPU:

```python
from clouditia import GPUSession

session = GPUSession("ck_your_api_key")

@session.remote
def compute_on_gpu(data, power=2):
    import torch
    tensor = torch.tensor(data, device='cuda', dtype=torch.float32)
    result = tensor ** power
    return result.cpu().tolist()

# Call the function - it runs on the remote GPU!
result = compute_on_gpu([1, 2, 3, 4, 5], power=2)
print(result)  # [1.0, 4.0, 9.0, 16.0, 25.0]
```

### Remote Function with Model

```python
@session.remote
def train_step(batch_data, learning_rate=0.01):
    import torch
    import torch.nn as nn

    # Create model (or load from checkpoint)
    model = nn.Sequential(
        nn.Linear(len(batch_data), 64),
        nn.ReLU(),
        nn.Linear(64, 1)
    ).cuda()

    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)

    # Training step
    x = torch.tensor(batch_data, dtype=torch.float32).cuda()
    output = model(x)
    loss = output.sum()

    optimizer.zero_grad()
    loss.backward()
    optimizer.step()

    return {"loss": loss.item()}

# Call it like a normal function
result = train_step([1.0, 2.0, 3.0, 4.0], learning_rate=0.001)
print(f"Loss: {result['loss']}")
```

### Async Remote Functions

```python
@session.remote(async_mode=True)
def long_training():
    import torch
    for epoch in range(100):
        print(f"Epoch {epoch}/100")
        # ... training code ...
    return {"status": "completed"}

# Returns an AsyncJob instead of waiting
job = long_training()
print(f"Job submitted: {job.job_id}")

# Wait for completion
result = job.wait(show_logs=True)
```

---

## Async Jobs (Long-Running Tasks)

For tasks that take hours or days, use async jobs:

### Submitting a Job

```python
# Submit a long-running job
job = session.submit("""
import torch
import time

print("Starting training...")
for epoch in range(100):
    print(f"Epoch {epoch + 1}/100")
    time.sleep(1)  # Simulate training

print("Training complete!")
torch.save({'epoch': 100}, '/workspace/checkpoint.pt')
""", name="my_training")

print(f"Job ID: {job.job_id}")
```

### Monitoring Progress

```python
import time

# Poll for status
while not job.is_done():
    status = job.status()
    print(f"Status: {status}")

    # View recent logs
    if status == "running":
        logs = job.logs(tail=10)
        print(logs)

    time.sleep(30)

print("Job finished!")
```

### Real-Time Log Streaming

```python
# View logs as they come in
while job.is_running():
    new_logs = job.logs(new_only=True)
    if new_logs.strip():
        print(new_logs, end='')
    time.sleep(5)
```

### Waiting for Completion

```python
# Wait with live log output
result = job.wait(show_logs=True)

# Or wait with timeout
try:
    result = job.wait(timeout=3600)  # 1 hour max
except TimeoutError:
    print("Job taking too long, cancelling...")
    job.cancel()
```

### Getting Results

```python
# Get the final result
result = job.result()

if result.success:
    print("Job completed successfully!")
    print(result.output)
else:
    print(f"Job failed: {result.error}")
```

### Listing Jobs

```python
# List all jobs
jobs = session.jobs()
for j in jobs:
    print(f"{j.name}: {j.status()}")

# List only running jobs
running_jobs = session.jobs(status="running")

# List completed jobs
completed_jobs = session.jobs(status="completed", limit=5)
```

### Cancelling Jobs

```python
if job.is_running():
    job.cancel()
    print("Job cancelled")
```

### Shell Jobs

```python
# Submit a shell command as an async job
job = session.submit(
    "pip install transformers && python /workspace/train.py",
    name="install_and_train",
    job_type="shell"
)
```

---

## Jupyter Magic

Use Clouditia directly in Jupyter notebooks with magic commands.

### Loading the Extension

```python
# In a Jupyter cell
%load_ext clouditia

# Set your API key
CLOUDITIA_API_KEY = "ck_your_api_key"
```

### Running Code on GPU

```python
%%clouditia
import torch
print(f"CUDA available: {torch.cuda.is_available()}")
print(f"GPU: {torch.cuda.get_device_name(0)}")

x = torch.randn(1000, 1000, device='cuda')
y = torch.randn(1000, 1000, device='cuda')
z = torch.matmul(x, y)
print(f"Result shape: {z.shape}")
```

### Specifying API Key Directly

```python
%%clouditia ck_your_api_key
print("Hello from GPU!")
```

### Async Mode in Jupyter

```python
%%clouditia --async
for epoch in range(100):
    print(f"Epoch {epoch}")
    # ... training code ...

# The job is submitted and _clouditia_job variable is set
```

```python
# Check job status
_clouditia_job.status()

# View logs
print(_clouditia_job.logs())
```

### Utility Magic Commands

```python
# Check session status
%clouditia_status

# List recent jobs
%clouditia_jobs

# List only running jobs
%clouditia_jobs running
```

---

## Error Handling

The SDK provides specific exceptions for different error types:

```python
from clouditia import (
    GPUSession,
    ClouditiaError,
    AuthenticationError,
    SessionError,
    ExecutionError,
    TimeoutError,
    CommandBlockedError
)

session = GPUSession("ck_your_api_key")

try:
    result = session.run("some_code()")
except AuthenticationError:
    print("Invalid API key")
except SessionError:
    print("Session not running or not accessible")
except ExecutionError as e:
    print(f"Code execution failed: {e}")
except TimeoutError:
    print("Execution timed out - consider using async jobs")
except CommandBlockedError:
    print("Command blocked by security filters")
except ClouditiaError as e:
    print(f"General error: {e}")
```

### Using raise_for_status()

```python
result = session.run("some_code()")
result.raise_for_status()  # Raises ExecutionError if failed
print(result.output)
```

---

## API Reference

### GPUSession

```python
GPUSession(
    api_key: str,
    base_url: str = "https://clouditia.com/code-editor",
    timeout: int = 120,
    poll_interval: int = 5
)
```

**Methods:**

| Method | Description |
|--------|-------------|
| `verify()` | Verify API key and get session info |
| `run(code, timeout=None, stream=True)` | Execute Python code |
| `exec(code, timeout=None)` | Execute without return value |
| `shell(command, timeout=None)` | Execute shell command |
| `start()` | Start a persistent session |
| `stop()` | Stop the persistent session |
| `set(name, value)` | Send variable to remote |
| `get(name)` | Retrieve variable from remote |
| `upload(local_path, remote_path, show_progress=True)` | Upload a file to remote session |
| `download(remote_path, local_path, show_progress=True)` | Download a file from remote session |
| `upload_folder(local_path, remote_path, exclude=None)` | Upload a folder to remote session |
| `download_folder(remote_path, local_path, exclude=None)` | Download a folder from remote session |
| `list_files(remote_path, pattern=None)` | List files in remote directory |
| `file_exists(remote_path)` | Check if a file exists on remote |
| `submit(code, name=None, job_type="python")` | Submit async job |
| `jobs(status=None, limit=10)` | List jobs |
| `gpu_info()` | Get GPU information |
| `remote(func)` | Decorator for remote functions |

**Properties:**

| Property | Description |
|----------|-------------|
| `is_persistent` | `True` if a persistent session is active |

### ExecutionResult

```python
ExecutionResult(
    output: str,      # stdout output
    result: Any,      # last expression value
    error: str,       # error message if failed
    exit_code: int,   # process exit code
    success: bool     # True if successful
)
```

**Methods:**

| Method | Description |
|--------|-------------|
| `raise_for_status()` | Raise exception if failed |
| `to_dict()` | Convert to dictionary |

### AsyncJob

```python
AsyncJob(session, job_id, name=None)
```

**Methods:**

| Method | Description |
|--------|-------------|
| `status()` | Get current status |
| `is_done()` | Check if finished |
| `is_running()` | Check if running |
| `is_pending()` | Check if pending |
| `logs(tail=50, new_only=False)` | Get logs |
| `result()` | Get final result |
| `cancel()` | Cancel the job |
| `wait(timeout=None, show_logs=False)` | Wait for completion |
| `get_info()` | Get detailed job info |

---

## Configuration

### Environment Variables

You can set the API key via environment variable:

```bash
export CLOUDITIA_API_KEY="ck_your_api_key"
```

```python
import os
from clouditia import GPUSession

session = GPUSession(os.environ["CLOUDITIA_API_KEY"])
```

### Custom Base URL

```python
session = GPUSession(
    "ck_your_api_key",
    base_url="https://custom.clouditia.com/code-editor"
)
```

### Timeouts

```python
# Set default timeout (seconds)
session = GPUSession("ck_your_api_key", timeout=300)

# Or per-request
result = session.run("long_computation()", timeout=600)
```

---

## Examples

### Training a Neural Network

```python
from clouditia import GPUSession

session = GPUSession("ck_your_api_key")

# Submit training job
job = session.submit("""
import torch
import torch.nn as nn
import torch.optim as optim

# Create model
model = nn.Sequential(
    nn.Linear(784, 256),
    nn.ReLU(),
    nn.Linear(256, 10)
).cuda()

optimizer = optim.Adam(model.parameters(), lr=0.001)
criterion = nn.CrossEntropyLoss()

# Training loop
for epoch in range(10):
    # Simulated batch
    x = torch.randn(64, 784).cuda()
    y = torch.randint(0, 10, (64,)).cuda()

    optimizer.zero_grad()
    output = model(x)
    loss = criterion(output, y)
    loss.backward()
    optimizer.step()

    print(f"Epoch {epoch+1}/10, Loss: {loss.item():.4f}")

# Save model
torch.save(model.state_dict(), '/workspace/model.pt')
print("Training complete!")
""", name="mnist_training")

# Wait with live logs
result = job.wait(show_logs=True)
```

### Data Processing Pipeline

```python
# Create workspace
session.shell("mkdir -p /workspace/data /workspace/output")

# Download data
session.shell("cd /workspace/data && wget https://example.com/data.csv")

# Process data
result = session.run("""
import pandas as pd

# Load and process data
df = pd.read_csv('/workspace/data/data.csv')
print(f"Loaded {len(df)} rows")

# Process...
df_processed = df.dropna()
print(f"After cleaning: {len(df_processed)} rows")

# Save
df_processed.to_csv('/workspace/output/processed.csv', index=False)
print("Saved to /workspace/output/processed.csv")
""")

print(result.output)
```

---

## Support

- **Documentation**: [https://clouditia.com/docsapisession](https://clouditia.com/docsapisession)
- **Email**: support@clouditia.com

---

## License

MIT License

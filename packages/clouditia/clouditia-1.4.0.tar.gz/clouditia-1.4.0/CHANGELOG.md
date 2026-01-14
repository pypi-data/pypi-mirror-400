# Changelog

All notable changes to the Clouditia SDK will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.4.0] - 2026-01-08

### Fixed
- Fixed `get()` returning "Unknown error" - now correctly retrieves variable values from persistent sessions
- Fixed error handling - Python exceptions are now properly detected as failures (`result.success = False`)
- Fixed persistent session REPL process management - no more duplicate processes
- Fixed expression evaluation in persistent sessions - last expression value is now returned
- Improved REPL daemonization with `setsid` for better process isolation

### Changed
- SDK now reads `result` field from API response for expression values
- Better error messages for execution failures

## [1.0.0] - 2026-01-05

### Added
- Initial release of Clouditia SDK
- `GPUSession` class for connecting to remote GPU sessions
- `run()` method for executing Python code
- `exec()` method for executing code without return value
- `shell()` method for executing shell commands
- `set()` and `get()` methods for variable transfer
- `submit()` method for async job submission
- `jobs()` method for listing async jobs
- `@session.remote` decorator for remote function execution
- `AsyncJob` class with status monitoring and log streaming
- `ExecutionResult` class for handling execution results
- Jupyter magic `%%clouditia` for notebook integration
- `%clouditia_status` and `%clouditia_jobs` line magics
- Comprehensive exception hierarchy:
  - `ClouditiaError` (base)
  - `AuthenticationError`
  - `SessionError`
  - `ExecutionError`
  - `TimeoutError`
  - `CommandBlockedError`
- Full type hints support
- Comprehensive documentation and examples

# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-10-16

### Added
- Initial release of AgentMonitor Python SDK
- `AgentMonitor` class for synchronous event tracking
- `AsyncAgentMonitor` class for async/await support
- `@track()` decorator for automatic function monitoring
- Context manager pattern via `track_event()`
- Manual event logging via `log_event()`
- Automatic event batching (configurable batch size)
- Background thread for periodic event flushing
- Exponential backoff retry logic (configurable)
- Thread-safe queue implementation
- Custom exception hierarchy (ConfigError, APIError, AuthenticationError, etc.)
- Data redaction support for sensitive fields
- Comprehensive error handling (never crashes user code)
- Type hints for all public APIs
- Full async/await support with aiohttp
- Detailed logging with debug mode
- Configuration validation
- TrackedEvent and AsyncTrackedEvent context managers

### Features
- Decorator pattern for zero-boilerplate monitoring
- Automatic input/output capture
- Automatic execution time measurement
- Automatic error tracking
- Configurable event types and metadata
- Selective input/output capture (privacy control)
- Cost tracking (USD)
- Latency tracking (milliseconds)
- Status tracking (success/error)
- Flexible configuration options
- Works with functions, methods, and class methods
- Support for nested function tracking
- Compatible with other decorators (stacking)

### Examples
- Basic usage example
- Async usage example
- Context manager example
- Manual tracking example
- Error handling example
- Advanced decorator patterns

### Documentation
- Comprehensive README with quick start guide
- API reference documentation in docstrings
- Multiple usage examples
- Configuration guide
- Error handling guide

### Developer Experience
- < 5 minute setup time
- Intuitive API design
- Sensible defaults
- Clear error messages
- IDE autocomplete support
- Type hints everywhere

[0.1.0]: https://github.com/agentmonitor/sdk-python/releases/tag/v0.1.0

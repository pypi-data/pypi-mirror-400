# Changelog

All notable changes to Orca SDK will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned

- Enhanced caching mechanisms
- Additional storage backends
- Improved middleware system
- More deployment adapters (Cloud Run, ECS, etc.)

## [1.0.4] - 2025-12-29

### Added

- **Lambda Adapter**: Complete AWS Lambda deployment support
  - Automatic HTTP, SQS, and Cron event handling
  - Event loop management for Python 3.11+
  - Automatic SQS queuing when `SQS_QUEUE_URL` exists
  - Production-ready templates and examples
- **Storage SDK**: Integrated file storage management
  - `OrcaStorage` client for unified storage operations
  - Support for bucket management, file operations, and permissions
- **Design Patterns**: Professional pattern implementations
  - `OrcaBuilder` and `SessionBuilder` for fluent interfaces
  - Context managers for resource management
  - Middleware system with chain of responsibility
- **Documentation**: Comprehensive guides for Lambda, Storage, and API

### Changed

- **Architecture**: Core refactoring to SOLID principles
- **Session Management**: Improved composition and cleaner API surface
- **Error Handling**: Enhanced custom exception hierarchy

### Improved

- **Type Safety**: 100% type hint coverage
- **Logging**: Professional logging configuration with rotation

## [1.0.0] - 2024-XX-XX

### Added

- Initial release
- Basic streaming functionality
- Real-time communication with Centrifugo
- Button rendering, loading indicators, and usage tracking

---

## Upgrade Guide

### Migrating to 1.0.4

#### Import Changes

```python
# Old
from orca.unified_handler import OrcaHandler

# New
from orca import OrcaHandler
```

#### Session API Improvements

The API has been moved to a more organized structure:

```python
# Old
session.start_loading("thinking")
session.button_link("Click", "https://example.com")

# New
session.loading.start("thinking")
session.button.link("Click", "https://example.com")
```

#### Backward Compatibility

The old flat session API still works but is deprecated and will be removed in future versions.

---

## Support

For questions or issues:

- Email: [support@orcaolatform.ai](mailto:support@orcaolatform.ai)
- GitHub: [orcapt/orca-pip](https://github.com/orcapt/orca-pip/issues)

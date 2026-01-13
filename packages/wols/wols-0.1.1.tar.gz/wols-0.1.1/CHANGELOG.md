# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.1] - 2026-01-05

### Added

- Container image published to GitHub Container Registry (ghcr.io)
- Containerfile for running WOLS CLI in containerized environments
- Multi-architecture support (linux/amd64, linux/arm64)

### Changed

- Release workflow now builds and publishes container images alongside PyPI packages

## [0.1.0] - 2026-01-04

### Added

- Initial release of WOLS Python library
- Core module with specimen creation, parsing, validation, and serialization
- Support for WOLS v1.1.0 specification
- Specimen types: CULTURE, SPAWN, SUBSTRATE, FRUITING, HARVEST
- Growth stages: INOCULATION, COLONIZATION, FRUITING, HARVEST
- JSON-LD serialization with `@context` and `@type` fields
- Compact URL format for small QR codes
- Optional QR code generation (PNG, SVG, base64)
- Optional QR code scanning
- Optional AES-256-GCM encryption for sensitive data
- CLI interface with create, validate, qr, and scan commands
- Full type annotations with PEP 561 support
- 80%+ test coverage

[Unreleased]: https://github.com/wemush/specimen-labels-py/compare/v0.1.1...HEAD
[0.1.1]: https://github.com/wemush/specimen-labels-py/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/wemush/specimen-labels-py/releases/tag/v0.1.0

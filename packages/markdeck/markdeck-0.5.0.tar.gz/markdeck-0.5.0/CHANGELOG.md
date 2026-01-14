# Changelog

All notable changes to MarkDeck will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.4.0] - 2026-01-04

### Added
- Two-column layout support using `:::columns` ... `|||` ... `:::` syntax
- Validation for malformed column markers in parser
- Comprehensive tests for two-column layout functionality
- Beige theme option

### Fixed
- Mermaid diagram rendering in two-column layouts
- Version sync between `pyproject.toml` and `__init__.py`
- Theme screenshot labels accounting for all 3 themes

### Changed
- Column processing now happens before markdown parsing to support mermaid diagrams
- Improved regex patterns for column marker detection
- Enhanced screenshot automation workflow

### Documentation
- Updated CLAUDE.md to reflect two-column rendering changes
- Added comprehensive documentation for screenshot methods
- Improved workflow documentation in `.github/workflows/`

## [0.3.0] - 2025-12-XX

### Added
- Grid view for slide navigation (press `O`)
- Theme cycling support (press `T`)
- Dark and light theme options
- Screenshot automation via GitHub Actions
- Comprehensive Claude Code documentation

### Changed
- Improved slide navigation and keyboard shortcuts
- Enhanced frontend architecture

## [0.2.0] - 2025-XX-XX

### Added
- Hot reload functionality with `--watch` flag
- Speaker notes support
- WebSocket-based live updates
- Progress bar

### Fixed
- Various bug fixes and improvements

## [0.1.0] - 2025-XX-XX

### Added
- Initial release
- Basic markdown presentation support
- FastAPI backend
- Syntax highlighting for code blocks
- Mermaid diagram support
- Math equations with KaTeX
- CLI interface with `markdeck present` command

[0.4.0]: https://github.com/orangewise/markdeck/releases/tag/v0.4.0
[0.3.0]: https://github.com/orangewise/markdeck/releases/tag/v0.3.0
[0.2.0]: https://github.com/orangewise/markdeck/releases/tag/v0.2.0
[0.1.0]: https://github.com/orangewise/markdeck/releases/tag/v0.1.0

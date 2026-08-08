# Changelog

All notable changes to ResearchFlow AI are documented here.

## [Unreleased]

### Added

- Project documentation set: contributing guide, code of conduct, architecture, security, design, and changelog.
- Updated SRS aligned with the current implementation.
- High-Level Design (`HLD.md`) and Low-Level Design (`LLD.md`) documents.

### Changed

- README now documents webhook mode, model fallback configuration, current limitations, and the actual Python requirement from `pyproject.toml`.
- SRS, architecture, and design docs now reference the dedicated HLD and LLD documents.

## [0.1.0] - 2026-08-08

### Added

- Google ADK coordinator agent.
- Academic web research sub-agent using Google Search.
- Academic future research synthesis sub-agent.
- FastAPI `/chat` endpoint.
- Telegram bot integration.
- Telegram webhook endpoint with optional secret validation.
- In-memory ADK session management.
- LLM/search model configuration with fallback handling.

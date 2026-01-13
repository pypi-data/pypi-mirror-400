# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.0] - 2026-01-04 (Day 1 - 33 Commits)

### 🎉 MAJOR: Real BOAMP Scraping Implemented
- Replaced mock data with real BOAMP.fr scraping
- Analyzed BOAMP structure (Angular.js with dynamic rendering)
- Implemented correct CSS selectors for tender extraction
- Created inspection tool for BOAMP structure analysis
- Successfully extracting: title, organisme, URL, date, region

### Added
- **CLI Tool** - Command-line interface (`python -m boamp`)
  - Search command with full filter support
  - Multiple output formats (table, JSON, CSV)
  - Export to file (--output)
  - Version command
- **Documentation (4,700+ lines total)**
  - CLI Guide (700+ lines)
  - API Reference (500+ lines)
  - FAQ (600+ lines)
  - Quick Start Guide (200+ lines)
  - Use Cases (300+ lines)
  - Launch Blog Post (1,500+ lines)
  - BOAMP Structure Analysis (REAL_BOAMP_NOTES.md)
  - Final Day 1 Recap (FINAL_RECAP_DAY1.md)
- **Tests & Quality**
  - +11 model tests (total: 19 tests)
  - 79% code coverage
  - Coverage reporting with pytest-cov
  - Performance benchmarks (benchmarks/speed_test.py)
  - Real scraping test script (examples/test_real_scraping.py)
- **Code Quality**
  - Black formatter integration
  - Ruff linter integration
  - All code formatted (PEP 8 compliant)
  - Zero linter warnings
- **Community Standards**
  - CODE_OF_CONDUCT.md
  - SECURITY.md
  - GitHub issue templates (bug, feature request)
  - Pull request template
  - AUTHORS.md
- **Project Infrastructure**
  - ROADMAP.md (12-week plan)
  - PyPI preparation (MANIFEST.in, sdist built)
  - Daily recap document (DAILY_RECAP_2026-01-04.md)
  - Final recap document (FINAL_RECAP_DAY1.md)
- **Tools**
  - BOAMP inspection tool (tools/inspect_boamp.py)
  - Captures HTML source and screenshots
  - Analyzes structure for correct selectors

### Changed
- **Pydantic v2 Migration** - Migrated from `class Config` to `ConfigDict`
- **README Enhanced** - Added CLI section, reorganized documentation links
- **Logging Improved** - More structured and informative log messages

### Fixed
- Bare except statements replaced with specific exceptions
- Boolean comparison in tests (use `assert x` instead of `assert x == True`)
- Pydantic v2 deprecation warnings resolved

## [0.1.0] - 2026-01-04

### Added
- Initial release
- Basic BOAMP scraper functionality
- Mock data for testing
- Examples and documentation
- MIT License

[Unreleased]: https://github.com/Ouailleme/boamp-scraper/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/Ouailleme/boamp-scraper/releases/tag/v0.1.0


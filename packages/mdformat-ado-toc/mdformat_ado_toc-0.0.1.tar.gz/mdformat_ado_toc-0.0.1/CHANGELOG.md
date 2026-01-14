# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.0.1] - 2026-01-07

### Added
- Initial release of mdformat-ado-toc plugin
- Preserves Azure DevOps `[[_TOC_]]` directive without escaping
- Custom markdown-it parser rule for TOC recognition
- Support for multiple TOC markers in one document
- Handles surrounding whitespace correctly
- Python type hints and modern Python syntax (>=3.10)
- Comprehensive test suite
- PyPI-compliant package structure

### Features
- Prevents `mdformat` from escaping `[[_TOC_]]` to `\[\[_TOC_\]\]`
- Works seamlessly with other mdformat plugins
- Command-line and Python API support

[0.0.1]: https://github.com/luish18/mdformat-ado-toc/releases/tag/v0.0.1


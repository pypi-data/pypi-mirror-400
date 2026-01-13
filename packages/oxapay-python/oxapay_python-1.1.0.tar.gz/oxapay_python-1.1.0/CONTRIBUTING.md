# Contributing to OxaPay Python SDK

Thanks for your interest in contributing to the OxaPay Python SDK 🙌  
This project is open-source and community contributions are welcome.

## General Rules

- **All code, comments, and documentation must be written in English**
- Follow Python best practices (PEP8, type hints where appropriate)
- Keep changes minimal and focused
- Do not introduce breaking changes without discussion

## Code Style

- Use `snake_case` for variables and methods
- Prefer explicit and readable code over clever abstractions
- Avoid mutable default arguments (e.g. `param={}`)
- Public APIs should remain backward-compatible

## Project Structure

- Source code lives under `src/oxapay_python/`
- Tests live under `tests/`
- New features should include tests where possible

## Error Handling

- All API errors must raise SDK-specific exceptions
- Do not expose raw `requests` exceptions directly
- Preserve API error messages returned by OxaPay

## HTTP & Networking

- Do not add automatic retries unless explicitly discussed
- Timeouts must always be configurable
- Keep request headers consistent with existing clients

## Documentation

- README should stay concise
- Do not duplicate API documentation
- Link methods to official OxaPay documentation instead

## Submitting Changes

1. Fork the repository
2. Create a feature or fix branch
3. Add or update tests if needed
4. Ensure CI passes
5. Open a Pull Request with a clear description

Thank you for helping improve OxaPay 🚀

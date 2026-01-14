# Contributing to prsdm

**Welcome! Thank you for your interest in contributing to prsdm.**

We appreciate any contributions you can make! Whether it's fixing bugs, adding new mathematical operations, improving code quality, or sharing ideas, every contribution helps make prsdm better.

## Ways to Contribute

### Report Bugs

If you've found a bug:

1. Check our [GitHub Issues](https://github.com/hypertic-ai/test/issues) to see if it's already reported
2. Create a new issue using the [bug report template](.github/ISSUE_TEMPLATE/bug_report.md)
3. Include steps to reproduce, expected vs actual behavior, and your environment details

### Suggest Features

Got an idea?

1. Check [open issues](https://github.com/hypertic-ai/test/issues?q=is%3Aissue+is%3Aopen+label%3Aenhancement) for existing requests
2. Start a [discussion](https://github.com/hypertic-ai/test/discussions) or use the [feature request template](.github/ISSUE_TEMPLATE/feature_request.md)
3. Describe your idea, why it's useful, and how it might work

### Contribute Code

1. Browse [open issues](https://github.com/hypertic-ai/test/issues) to find something to work on
2. Let us know if you're working on an issue to avoid duplicate work
3. Follow the development workflow below

## Development Workflow

### Setup

1. Fork and clone the repository
2. Install dependencies: `make sync`
3. Verify setup: `make check`

**Requirements:** Python 3.10+ and [uv](https://docs.astral.sh/uv/getting-started/installation/)

### Making Changes

1. Create a branch: `git checkout -b feat/your-feature-name` or `fix/your-bug-fix`
2. Make your changes and add tests
3. Format code: `make format`
4. Run checks: `make check` (runs formatting, linting, type checking, and tests)

### Code Standards

- **Formatting/Linting**: `ruff` (run `make format`)
- **Type Checking**: `mypy` (run `make mypy`)
- **Line Length**: 100 characters max
- **Tests**: Required for new features (95%+ coverage goal)
- **Commits**: Use conventional format (e.g., `feat: add new operation`, `fix: resolve bug`)

### Submitting a Pull Request

1. Ensure all checks pass: `make check`
2. Push your branch and create a PR on GitHub
3. Fill out the PR template and link related issues
4. Complete the checklist in the PR template

## Code of Conduct

This project follows a [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## Getting Help

- [Documentation](https://github.com/hypertic-ai/test#readme)
- [Issues](https://github.com/hypertic-ai/test/issues)
- [Discussions](https://github.com/hypertic-ai/test/discussions)

## License

This project is licensed under the terms of the [Apache License 2.0](LICENSE).

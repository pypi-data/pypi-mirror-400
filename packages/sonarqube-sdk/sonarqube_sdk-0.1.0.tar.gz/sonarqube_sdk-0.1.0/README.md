# SonarQube SDK

[![PyPI version](https://badge.fury.io/py/sonarqube-sdk.svg)](https://badge.fury.io/py/sonarqube-sdk)
[![Python versions](https://img.shields.io/pypi/pyversions/sonarqube-sdk.svg)](https://pypi.org/project/sonarqube-sdk/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Documentation Status](https://readthedocs.org/projects/sonarqube-sdk/badge/?version=latest)](https://sonarqube-sdk.readthedocs.io/en/latest/?badge=latest)

A fully-typed Python SDK for the SonarQube API.

## Features

- **Full API Coverage**: Support for all 30+ SonarQube API domains
- **Type Safety**: Complete type hints with Pydantic models
- **Authentication**: Support for both token and basic authentication
- **Async Support**: Built on httpx for modern async/sync HTTP handling
- **Python 3.9+**: Compatible with Python 3.9 through 3.13

## Installation

```bash
pip install sonarqube-sdk
```

Or with [uv](https://github.com/astral-sh/uv):

```bash
uv add sonarqube-sdk
```

## Quick Start

```python
from sonarqube import SonarQubeClient

# Initialize client with token authentication
client = SonarQubeClient(
    base_url="https://sonarqube.example.com",
    token="your-token"
)

# Or with basic authentication
client = SonarQubeClient(
    base_url="https://sonarqube.example.com",
    username="admin",
    password="admin"
)

# Create an application
app = client.applications.create(
    name="My Application",
    key="my-app",
    visibility="private"
)

# Add a project to the application
client.applications.add_project(
    application="my-app",
    project="my-project"
)

# Search for projects
projects = client.projects.search(q="backend")
for project in projects.components:
    print(f"Project: {project.name} ({project.key})")

# Get issues
issues = client.issues.search(
    project_keys=["my-project"],
    severities=["CRITICAL", "BLOCKER"]
)
for issue in issues.issues:
    print(f"Issue: {issue.message}")
```

## API Domains

The SDK provides access to all SonarQube API domains through a namespace pattern:

| Domain | Description |
|--------|-------------|
| `client.applications` | Manage applications |
| `client.projects` | Manage projects |
| `client.issues` | Manage issues |
| `client.rules` | Manage rules |
| `client.qualitygates` | Manage quality gates |
| `client.qualityprofiles` | Manage quality profiles |
| `client.users` | Manage users |
| `client.user_tokens` | Manage user tokens |
| `client.permissions` | Manage permissions |
| `client.settings` | Manage settings |
| ... | And 20+ more domains |

## Documentation

Full documentation is available at [https://sonarqube-sdk.readthedocs.io](https://sonarqube-sdk.readthedocs.io)

## Development

### Setup

```bash
# Clone the repository
git clone https://github.com/silasvasconcelos/sonarqube-sdk.git
cd sonarqube-sdk

# Install development dependencies
make dev
```

### Common Commands

```bash
make help          # Show all available commands
make test          # Run tests
make test-cov      # Run tests with coverage
make lint          # Run linter
make format        # Format code
make type          # Run type checker
make security      # Run security checks
make check         # Run all checks
make tox           # Run tests on all Python versions
make docs          # Build documentation
make build         # Build package
```

### Testing

```bash
# Run all tests
make test

# Run tests with coverage
make test-cov

# Run tests on all Python versions
make tox

# Run specific Python version
make tox-py312
```

## Contributing

Contributions are welcome! Please read our [Contributing Guide](CONTRIBUTING.md) for details.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for a history of changes.


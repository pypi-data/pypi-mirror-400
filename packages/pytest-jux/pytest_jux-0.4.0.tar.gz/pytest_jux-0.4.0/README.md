# pytest-jux

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python Version](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![pytest](https://img.shields.io/badge/pytest-7.4%2B%20%7C%208.x-blue.svg)](https://pytest.org/)
[![codecov](https://codecov.io/gh/jrjsmrtn/pytest-jux/branch/main/graph/badge.svg)](https://codecov.io/gh/jrjsmrtn/pytest-jux)
[![SLSA 2](https://slsa.dev/images/gh-badge-level2.svg)](https://slsa.dev/spec/v1.0/levels#build-l2)
[![Security](https://img.shields.io/badge/security-framework-green.svg)](docs/security/SECURITY.md)

_A pytest plugin for signing and publishing JUnit XML test reports to the Jux REST API_

## Overview

pytest-jux is a **client-side pytest plugin** that automatically signs JUnit XML test reports using XML digital signatures (XMLDSig) and publishes them to a Jux REST API backend for storage and analysis. It enables system administrators, integrators, and infrastructure engineers to maintain a chain-of-trust for test results across local and distributed environments.

### Architecture

pytest-jux is the **client component** in a client-server architecture:

- **pytest-jux (this project)**: Client-side plugin for signing and publishing test reports
- **Jux API Server** (separate project): Server-side backend for storing, querying, and visualizing reports

This separation allows pytest-jux to be lightweight and focused on test report signing, while the Jux API Server handles data persistence, deduplication, and web interfaces.

## Features

### Client-Side Features (pytest-jux)

- **Automatic Report Signing**: Signs JUnit XML reports with XML digital signatures after test execution
- **XML Canonicalization**: Uses C14N for generating canonical hashes
- **Chain-of-Trust**: Cryptographic signatures ensure report integrity and provenance
- **REST API Publishing**: Publishes signed reports to Jux API backend
- **Local Storage & Caching**: XDG-compliant storage with offline queue for unreliable networks
- **Flexible Storage Modes**: LOCAL (filesystem only), API (server only), BOTH (dual), CACHE (offline queue)
- **Configuration Management**: Multi-source configuration (CLI, environment, files) with precedence
- **pytest Integration**: Seamless integration via pytest hooks (post-session processing)
- **Standalone CLI Tools**: Key generation, signing, verification, inspection, cache, and config utilities
- **Environment Metadata**: Captures test environment context (hostname, user, platform)
- **Custom Metadata Support**: Add custom metadata to reports via pytest-metadata integration
- **Security Framework**: Comprehensive security with automated scanning and threat modeling

### Server-Side Features (Jux API Server)

The following features are provided by the **Jux API Server** (separate project):

- **Report Storage**: Persistent storage in SQLite (local) or PostgreSQL (distributed)
- **Duplicate Detection**: Canonical hash-based deduplication prevents redundant storage
- **Signature Verification**: Server-side validation of XMLDSig signatures
- **Query API**: REST API for retrieving and filtering stored reports
- **Web UI**: Browser-based interface for visualizing test results
- **Multi-tenancy**: Support for multiple projects and users

## Security

pytest-jux implements a comprehensive security framework with **SLSA Build Level 2** compliance:

### Supply Chain Security (SLSA L2)

[![SLSA 2](https://slsa.dev/images/gh-badge-level2.svg)](https://slsa.dev/spec/v1.0/levels#build-l2)

All pytest-jux releases include cryptographic provenance attestations:

- ✅ **Build Integrity**: Packages built on GitHub Actions (not developer workstations)
- ✅ **Source Traceability**: Cryptographic link to exact source code commit
- ✅ **Tamper Detection**: Any modification invalidates the signature
- ✅ **Independent Verification**: Verify packages with `slsa-verifier`

**Verify a release:**
```bash
# Install SLSA verifier
go install github.com/slsa-framework/slsa-verifier/v2/cli/slsa-verifier@latest

# Download and verify
pip download pytest-jux==0.2.0 --no-deps
curl -L -O https://github.com/jrjsmrtn/pytest-jux/releases/download/v0.2.0/pytest-jux-0.2.0.intoto.jsonl

slsa-verifier verify-artifact \
  --provenance-path pytest-jux-0.2.0.intoto.jsonl \
  --source-uri github.com/jrjsmrtn/pytest-jux \
  pytest_jux-0.2.0-py3-none-any.whl
```

See [SLSA Verification Guide](docs/security/SLSA_VERIFICATION.md) for complete instructions.

### Security Framework

- **Automated Scanning**: pip-audit, Ruff (security rules), Safety, Trivy
- **Threat Modeling**: STRIDE methodology with 19 identified threats
- **Cryptographic Standards**: NIST-compliant algorithms (RSA-SHA256, ECDSA-SHA256)
- **Supply Chain**: SLSA L2, Dependabot, OpenSSF Scorecard
- **Vulnerability Reporting**: Coordinated disclosure with 48-hour response time

See [Security Policy](docs/security/SECURITY.md) for vulnerability reporting and [Security Framework](docs/security/IMPLEMENTATION_SUMMARY.md) for complete details.

## Architecture Documentation

This project uses Architecture Decision Records (ADRs) to track significant architectural decisions:

- **[ADR-0001](docs/adr/0001-record-architecture-decisions.md)**: Record architecture decisions
- **[ADR-0002](docs/adr/0002-adopt-development-best-practices.md)**: Adopt development best practices
- **[ADR-0003](docs/adr/0003-use-python3-pytest-lxml-signxml-sqlalchemy-stack.md)**: Use Python 3 with pytest, lxml, signxml, and SQLAlchemy stack
- **[ADR-0004](docs/adr/0004-adopt-apache-license-2.0.md)**: Adopt Apache License 2.0
- **[ADR-0005](docs/adr/0005-adopt-python-ecosystem-security-framework.md)**: Adopt Python Ecosystem Security Framework
- **[ADR-0006](docs/adr/0006-adopt-slsa-build-level-2-compliance.md)**: Adopt SLSA Build Level 2 Compliance

See the [docs/adr/](docs/adr/) directory for complete decision history.

## Requirements

- Python 3.11+
- pytest 7.4+ or 8.x
- Supported OS: Debian 12/13, latest openSUSE, latest Fedora

## Installation

```bash
# From PyPI (when published)
uv pip install pytest-jux

# From source (development)
cd pytest-jux
uv pip install -e ".[dev,security]"
```

## Usage

### Basic Usage

```bash
# Run tests with JUnit XML generation and auto-publish
pytest --junit-xml=report.xml \
       --jux-publish \
       --jux-api-url=https://jux.example.com/api \
       --jux-key=~/.jux/private_key.pem
```

### Configuration via pytest.ini

```ini
[pytest]
addopts = --junit-xml=report.xml
jux_api_url = https://jux.example.com/api
jux_key_path = ~/.jux/private_key.pem
```

### Plugin Options

- `--jux-publish`: Enable pytest-jux plugin (default: disabled)
- `--jux-api-url URL`: Jux REST API endpoint
- `--jux-key PATH`: Path to private key for signing (PEM format)
- `--jux-storage-mode MODE`: Storage mode (local, api, both, cache)
- `--jux-storage-path PATH`: Custom storage directory path

### Adding Custom Metadata

pytest-jux integrates with pytest-metadata to add custom metadata to your test reports:

```bash
# Add metadata via command line
pytest --junit-xml=report.xml \
       --jux-sign \
       --jux-key ~/.jux/signing_key.pem \
       --metadata ci_build_id 12345 \
       --metadata environment production
```

The metadata appears as property tags in the JUnit XML:

```xml
<testsuite>
  <properties>
    <property name="ci_build_id" value="12345"/>
    <property name="environment" value="production"/>
  </properties>
  ...
</testsuite>
```

See [How to Add Metadata to Reports](docs/howto/add-metadata-to-reports.md) for complete documentation including CI/CD integration, JSON metadata, and programmatic usage.

## Storage & Caching

pytest-jux provides flexible storage options for test reports, supporting both local filesystem storage and API publishing. This enables offline operation, network-resilient workflows, and local inspection of test results.

### Storage Modes

pytest-jux supports four storage modes:

- **LOCAL**: Store reports locally only (no API publishing)
- **API**: Publish to API only (no local storage)
- **BOTH**: Store locally AND publish to API
- **CACHE**: Store locally, publish when API available (offline queue)

### Storage Location

Reports are stored in XDG-compliant directories:

- **macOS**: `~/Library/Application Support/jux/reports/`
- **Linux**: `~/.local/share/jux/reports/`
- **Windows**: `%LOCALAPPDATA%\jux\reports\`

Custom storage paths can be specified via `--jux-storage-path` or `JUX_STORAGE_PATH` environment variable.

### Storage Examples

**Local storage only** (no API required):
```bash
pytest --junit-xml=report.xml \
       --jux-enabled \
       --jux-sign \
       --jux-key=~/.jux/private_key.pem \
       --jux-storage-mode=local
```

**API publishing with local backup**:
```bash
pytest --junit-xml=report.xml \
       --jux-enabled \
       --jux-sign \
       --jux-key=~/.jux/private_key.pem \
       --jux-api-url=https://jux.example.com/api \
       --jux-storage-mode=both
```

**Offline queue mode** (auto-publish when API available):
```bash
pytest --junit-xml=report.xml \
       --jux-enabled \
       --jux-sign \
       --jux-key=~/.jux/private_key.pem \
       --jux-api-url=https://jux.example.com/api \
       --jux-storage-mode=cache
```

### Cache Management

The `jux-cache` command provides tools for inspecting and managing cached reports.

**List cached reports**:
```bash
# Text output
jux-cache list

# JSON output
jux-cache list --json
```

**Show report details**:
```bash
# View specific report
jux-cache show sha256:abc123...

# JSON output
jux-cache show sha256:abc123... --json
```

**View cache statistics**:
```bash
# Text output
jux-cache stats

# JSON output
jux-cache stats --json
```

**Clean old reports**:
```bash
# Dry run (preview what would be deleted)
jux-cache clean --days 30 --dry-run

# Actually delete reports older than 30 days
jux-cache clean --days 30
```

**Custom storage path**:
```bash
jux-cache --storage-path /custom/path list
```

## Configuration Management

pytest-jux supports multi-source configuration with precedence: CLI arguments > environment variables > configuration files > defaults.

### Configuration Sources

Configuration can be loaded from:

1. **Command-line arguments** (highest precedence)
2. **Environment variables** (prefixed with `JUX_`)
3. **Configuration files**:
   - `~/.jux/config` (user-level)
   - `.jux.conf` (project-level)
   - `pytest.ini` (pytest configuration)
   - `/etc/jux/config` (system-level, Linux/Unix)

### Configuration File Format

Configuration files use INI format with a `[jux]` section:

```ini
[jux]
# Core settings
enabled = true
sign = true
publish = false

# Storage settings
storage_mode = local
# storage_path = ~/.local/share/jux/reports

# Signing settings
# key_path = ~/.jux/signing_key.pem
# cert_path = ~/.jux/signing_key.crt

# API settings
# api_url = https://jux.example.com/api/v1/reports
# api_key = your-api-key-here
```

### Configuration Management Commands

The `jux-config` command provides tools for managing configuration.

**List all configuration options**:
```bash
# Text output
jux-config list

# JSON output
jux-config list --json
```

**Dump current effective configuration**:
```bash
# Text output (shows sources)
jux-config dump

# JSON output
jux-config dump --json
```

**View configuration files**:
```bash
# View specific file
jux-config view ~/.jux/config

# View all configuration files
jux-config view --all
```

**Initialize configuration file**:
```bash
# Create minimal config at default path (~/.jux/config)
jux-config init

# Create full config with all options
jux-config init --template full

# Create at custom path
jux-config init --path /custom/path/config

# Force overwrite existing file
jux-config init --force
```

**Validate configuration**:
```bash
# Basic validation
jux-config validate

# Strict validation (check dependencies)
jux-config validate --strict

# JSON output
jux-config validate --json
```

### Environment Variables

All configuration options can be set via environment variables:

```bash
export JUX_ENABLED=true
export JUX_SIGN=true
export JUX_KEY_PATH=~/.jux/private_key.pem
export JUX_STORAGE_MODE=local
export JUX_API_URL=https://jux.example.com/api
export JUX_API_KEY=your-api-key-here
```

### Configuration Examples

**Minimal configuration** (local storage only):
```ini
[jux]
enabled = true
sign = false
storage_mode = local
```

**Development configuration** (local storage + API publishing):
```ini
[jux]
enabled = true
sign = true
key_path = ~/.jux/dev_key.pem
storage_mode = both
api_url = http://localhost:4000/api/v1/reports
```

**Production configuration** (signed reports with offline queue):
```ini
[jux]
enabled = true
sign = true
key_path = ~/.jux/prod_key.pem
cert_path = ~/.jux/prod_key.crt
storage_mode = cache
api_url = https://jux.example.com/api/v1/reports
```

## CLI Tools

pytest-jux provides standalone CLI commands for key management, signing, verification, and administration:

**Key generation**:
```bash
jux-keygen --output ~/.jux/private_key.pem --algorithm rsa
```

**Offline signing**:
```bash
jux-sign report.xml --key ~/.jux/private_key.pem --output signed_report.xml
```

**Signature verification**:
```bash
jux-verify signed_report.xml
```

**Report inspection**:
```bash
jux-inspect report.xml
```

**Cache management**:
```bash
jux-cache list
jux-cache show sha256:abc123...
jux-cache stats
jux-cache clean --days 30
```

**Configuration management**:
```bash
jux-config list
jux-config dump
jux-config init
jux-config validate
```

See CLI tool documentation for complete usage details.

## Documentation

**Complete Documentation Index**: See **[docs/INDEX.md](docs/INDEX.md)** for a complete map of all available documentation.

This project follows the [Diátaxis framework](https://diataxis.fr/), organizing documentation into four categories:

### 📚 Tutorials (Learning-Oriented)

Step-by-step guides to learn pytest-jux from beginner to advanced:

- **[Quick Start](docs/tutorials/quick-start.md)** - Get started in 5 minutes
- **[Setting Up Signing Keys](docs/tutorials/setting-up-signing-keys.md)** - Generate and configure cryptographic keys (10 minutes)
- **[First Signed Report](docs/tutorials/first-signed-report.md)** - Complete beginner walkthrough with tamper detection (15-20 min)
- **[Integration Testing](docs/tutorials/integration-testing.md)** - Multi-environment setup and CI/CD integration (30-45 min)
- **[Custom Signing Workflows](docs/tutorials/custom-signing-workflows.md)** - Programmatic API usage and batch processing (30-40 min)

### 🛠️ How-To Guides (Problem-Oriented)

Practical solutions to specific problems:

**Key Management:**
- [Rotate Signing Keys](docs/howto/rotate-signing-keys.md)
- [Secure Key Storage](docs/howto/secure-key-storage.md)
- [Backup & Restore Keys](docs/howto/backup-restore-keys.md)

**Storage & Configuration:**
- [Migrate Storage Paths](docs/howto/migrate-storage-paths.md)
- [Manage Report Cache](docs/howto/manage-report-cache.md)
- [Choosing Storage Modes](docs/howto/choosing-storage-modes.md)
- [Multi-Environment Configuration](docs/howto/multi-environment-config.md)

**Integration:**
- [CI/CD Deployment](docs/howto/ci-cd-deployment.md) - GitHub Actions, GitLab CI, Jenkins
- [Integrate with pytest Plugins](docs/howto/integrate-pytest-plugins.md)
- [Add Metadata to Reports](docs/howto/add-metadata-to-reports.md)

**Troubleshooting:**
- [Troubleshooting Guide](docs/howto/troubleshooting.md) - Diagnose and fix common issues

### 📖 Reference (Information-Oriented)

Complete technical reference documentation:

**API Reference:**
- [API Index](docs/reference/api/index.md) - Overview of all modules
- [Canonicalizer API](docs/reference/api/canonicalizer.md) - XML canonicalization and hashing
- [Signer API](docs/reference/api/signer.md) - XMLDSig signature generation
- [Verifier API](docs/reference/api/verifier.md) - Signature verification
- [Storage API](docs/reference/api/storage.md) - Report caching and storage
- [Config API](docs/reference/api/config.md) - Configuration management
- [Metadata API](docs/reference/api/metadata.md) - Environment metadata collection
- [Plugin API](docs/reference/api/plugin.md) - pytest plugin hooks

**CLI Reference:**
- [CLI Index](docs/reference/cli/index.md) - All CLI commands with examples

**Configuration:**
- [Configuration Reference](docs/reference/configuration.md) - All configuration options
- [Error Code Reference](docs/reference/error-codes.md) - Complete error catalog with solutions

### 💡 Explanation (Understanding-Oriented)

Conceptual understanding and design discussions:

- [Understanding pytest-jux](docs/explanation/understanding-pytest-jux.md) - High-level overview and use cases
- [Architecture](docs/explanation/architecture.md) - System design, components, and design decisions
- [Security](docs/explanation/security.md) - Why sign test reports, threat model, security best practices
- [Performance](docs/explanation/performance.md) - Performance characteristics, benchmarks, optimization

### 🔒 Security Documentation

- [Security Policy](docs/security/SECURITY.md) - Vulnerability reporting
- [Threat Model](docs/security/THREAT_MODEL.md) - Threat analysis and mitigation
- [Cryptographic Standards](docs/security/CRYPTO_STANDARDS.md) - Algorithms and standards
- [SLSA Verification](docs/security/SLSA_VERIFICATION.md) - Supply chain security

### 🆘 Quick Navigation

**I want to...**
- **Get started** → [Quick Start](docs/tutorials/quick-start.md) (5 minutes)
- **Set up CI/CD** → [CI/CD Deployment](docs/howto/ci-cd-deployment.md)
- **Troubleshoot issues** → [Troubleshooting Guide](docs/howto/troubleshooting.md)
- **Look up CLI commands** → [CLI Reference](docs/reference/cli/index.md)
- **Understand security** → [Security Explanation](docs/explanation/security.md)
- **Browse all docs** → [Complete Documentation Index](docs/INDEX.md)

## Development

### Setup

```bash
# Clone repository
git clone https://github.com/jrjsmrtn/pytest-jux.git
cd pytest-jux

# Create virtual environment
uv venv
source .venv/bin/activate  # or: .venv\Scripts\activate on Windows

# Install development dependencies
uv pip install -e ".[dev,security]"

# Install pre-commit hooks
pre-commit install
```

### Development Commands

#### Code Quality

```bash
# Format code
make format

# Lint code
make lint

# Type checking
make type-check

# All quality checks
make quality
```

#### Testing

```bash
# Run all tests
make test

# Run tests with coverage
make test-cov

# Run security tests
make test-security
```

#### Security

```bash
# Run security scanners
make security-scan

# Run security test suite
make security-test

# Complete security validation
make security-full
```

#### Architecture Validation

```bash
# Validate C4 DSL architecture model
podman run --rm -v "$(pwd)/docs/architecture:/usr/local/structurizr" \
  structurizr/cli validate -workspace workspace.dsl

# Generate architecture diagrams
podman run --rm -p 8080:8080 \
  -v "$(pwd)/docs/architecture:/usr/local/structurizr" structurizr/lite
# Open http://localhost:8080
```

### Project Structure

```
pytest-jux/
├── pytest_jux/              # Plugin source code
│   ├── __init__.py
│   ├── plugin.py           # pytest hooks
│   ├── signer.py           # XML signing
│   ├── verifier.py         # Signature verification
│   ├── canonicalizer.py    # C14N operations
│   ├── config.py           # Configuration management (Sprint 3)
│   ├── metadata.py         # Environment metadata (Sprint 3)
│   ├── storage.py          # Local storage & caching (Sprint 3)
│   ├── api_client.py       # REST API client (Sprint 3 - postponed)
│   └── commands/           # CLI commands
│       ├── keygen.py       # Key generation
│       ├── sign.py         # Offline signing
│       ├── verify.py       # Signature verification
│       ├── inspect.py      # Report inspection
│       ├── cache.py        # Cache management (Sprint 3)
│       ├── config_cmd.py   # Config management (Sprint 3)
│       └── publish.py      # Manual publishing (Sprint 3 - postponed)
├── tests/                   # Test suite
│   ├── test_plugin.py
│   ├── test_signer.py
│   ├── test_verifier.py
│   ├── test_canonicalizer.py
│   ├── test_config.py      # Config tests (Sprint 3)
│   ├── test_metadata.py    # Metadata tests (Sprint 3)
│   ├── test_storage.py     # Storage tests (Sprint 3)
│   ├── commands/           # CLI command tests
│   │   ├── test_cache.py   # Cache command tests (Sprint 3)
│   │   └── test_config_cmd.py  # Config command tests (Sprint 3)
│   ├── security/           # Security tests
│   └── fixtures/           # JUnit XML fixtures & test keys
├── docs/                    # Documentation
│   ├── tutorials/          # Learning-oriented
│   ├── howto/             # Problem-oriented
│   ├── reference/         # Information-oriented
│   ├── explanation/       # Understanding-oriented
│   ├── adr/              # Architecture decisions
│   ├── architecture/     # C4 DSL models
│   ├── sprints/          # Sprint documentation
│   └── security/         # Security documentation
├── .github/
│   └── workflows/
│       └── security.yml    # Security scanning workflow
├── LICENSE                 # Apache License 2.0
├── NOTICE                  # Copyright notices
├── Makefile                # Development commands
├── pyproject.toml          # Project metadata
└── README.md              # This file
```

**Note**: This project does **not** include database models (`models.py`) or database integration. These are handled by the Jux API Server.

## Architecture Overview

### Client-Server Architecture

```
┌─────────────────────────────────┐         ┌──────────────────────────┐
│   pytest-jux (Client)           │         │  Jux API Server          │
│                                 │         │                          │
│  1. Run tests                   │         │  6. Receive signed XML   │
│  2. Generate JUnit XML          │         │  7. Verify signature     │
│  3. Canonicalize (C14N)         │  HTTP   │  8. Check for duplicates │
│  4. Sign with XMLDSig           │ ─POST─> │  9. Store in database    │
│  5. Publish to API              │         │ 10. Return status        │
│                                 │         │                          │
│  • XML signing                  │         │  • Report storage        │
│  • Environment metadata         │         │  • Duplicate detection   │
│  • API client                   │         │  • Signature verification│
│                                 │         │  • Query API             │
│                                 │         │  • Web UI                │
└─────────────────────────────────┘         └──────────────────────────┘
```

### pytest Plugin Integration

pytest-jux integrates with pytest via the `pytest_sessionfinish` hook, processing JUnit XML reports after test execution completes.

### Client-Side Workflow

1. **Generate**: pytest creates JUnit XML report (`--junit-xml`)
2. **Canonicalize**: Convert XML to canonical form (C14N) and compute SHA-256 hash
3. **Sign**: Generate XMLDSig signature using private key
4. **Capture Metadata**: Collect environment information (hostname, platform, etc.)
5. **Publish**: POST signed report + metadata to Jux REST API

### Server-Side Processing (Jux API Server)

6. **Receive**: Accept signed XML report via REST API
7. **Verify**: Validate XMLDSig signature
8. **Deduplicate**: Check canonical hash against existing reports
9. **Store**: Save to database (SQLite or PostgreSQL)
10. **Index**: Make report queryable via API and Web UI

### C4 DSL Architecture Models

The project's architecture is documented using C4 DSL models in `docs/architecture/`. See the architecture documentation for:

- System context: pytest-jux in the Jux ecosystem
- Container view: Plugin components and REST API integration
- Component view: Internal module structure

## AI-Assisted Development Notes

### AI Collaboration Context

- This project follows AI-Assisted Project Orchestration patterns
- ADRs provide AI context across development sessions
- Sprint documentation maintains development continuity (see `docs/sprints/`)
- C4 DSL models provide visual architecture context
- TDD approach guides AI-assisted test and implementation generation

### Development Practices Integration

- AI assistance for boilerplate generation (pytest hooks, SQLAlchemy models)
- Human review required for cryptographic code (security-critical)
- Quality gates: all tests pass, type checking clean, code coverage >85%
- Context management: ADRs and sprint docs enable session continuity

## Contributing

Contributions welcome! Please:

1. Read the [Architecture Decision Records](docs/adr/) to understand project direction
2. Follow the [development best practices](docs/adr/0002-adopt-development-best-practices.md)
3. Review [security guidelines](docs/security/SECURITY.md) for security-sensitive changes
4. Ensure all tests pass and coverage remains >85%
5. Run security scanners: `make security-full`
6. Update documentation for new features
7. Use conventional commits for clear changelog generation

## License

Copyright 2025 Georges Martin

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

See [LICENSE](LICENSE) for the full license text.

## Related Projects

### Jux API Server (Separate Project)

The **Jux API Server** is the server-side component that works with pytest-jux. It is a separate project that provides:

**Core Functionality:**
- REST API endpoints for receiving signed test reports
- XMLDSig signature verification
- Report storage in SQLite (local) or PostgreSQL (distributed)
- Canonical hash-based duplicate detection
- Query API for retrieving stored reports

**User Interfaces:**
- Web UI for browsing and visualizing test results
- CLI tools for querying reports
- API documentation (OpenAPI/Swagger)

**Technology Stack:**
- Elixir/Phoenix framework
- PostgreSQL or SQLite database
- RESTful API design

**Deployment Options:**
- Local development (SQLite)
- Single-server deployment (PostgreSQL)
- Distributed/multi-tenant deployment (PostgreSQL cluster)

For more information about the Jux API Server, refer to its separate repository and documentation.

## Releases

**Latest Release**: [v0.3.0 - Metadata Integration](https://github.com/jrjsmrtn/pytest-jux/releases/tag/v0.3.0) (2025-10-24)

**Release Notes**: See [docs/release-notes/](docs/release-notes/) for detailed release notes for all versions.

**Changelog**: See [CHANGELOG.md](CHANGELOG.md) for a complete version history.

## Support

- Documentation: [docs/](docs/)
- Security: [Security Policy](docs/security/SECURITY.md)
- Issues: [GitHub Issues](https://github.com/jrjsmrtn/pytest-jux/issues)
- Discussions: [GitHub Discussions](https://github.com/jrjsmrtn/pytest-jux/discussions)

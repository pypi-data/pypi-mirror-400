# SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
# SPDX-License-Identifier: Apache-2.0

"""Configuration management command for pytest-jux."""

import argparse
import json
import sys
from pathlib import Path

from pytest_jux.config import ConfigSchema, ConfigurationManager


def cmd_list(args: argparse.Namespace) -> int:
    """List all configuration options.

    Args:
        args: Command-line arguments

    Returns:
        Exit code (0 = success)
    """
    schema = ConfigSchema.get_schema()

    if args.json:
        # JSON output
        output = {"options": schema}
        print(json.dumps(output, indent=2, default=str))
    else:
        # Text output
        print("Available Configuration Options:")
        print()
        for key, field_info in schema.items():
            field_type = field_info["type"]
            default = field_info["default"]
            description = field_info.get("description", "")

            # Format type
            if field_type == "enum":
                choices = "|".join(field_info.get("choices", []))
                type_str = f"{field_type}:{choices}"
            else:
                type_str = field_type

            # Format default
            if default is None:
                default_str = "(not set)"
            else:
                default_str = f"[default: {default}]"

            print(f"  {key}")
            print(f"    Type:        {type_str}")
            print(f"    Default:     {default_str}")
            if description:
                print(f"    Description: {description}")
            print()

    return 0


def cmd_dump(args: argparse.Namespace) -> int:
    """Dump current effective configuration.

    Args:
        args: Command-line arguments

    Returns:
        Exit code (0 = success)
    """
    config = ConfigurationManager()

    # Load from environment
    config.load_from_env()

    # Load from config files (skip non-INI files)
    for config_file in _find_config_files():
        # Only load .conf and .ini files
        if config_file.suffix in [".conf", ".ini"]:
            config.load_from_file(config_file)

    if args.json:
        # JSON output
        dump = config.dump()
        print(json.dumps(dump, indent=2, default=str))
    else:
        # Text output with sources
        print("Current Configuration:")
        print()

        dump_with_sources = config.dump(include_sources=True)
        for key, info in dump_with_sources.items():
            value = info["value"]
            source = info["source"]

            # Format value
            if value is None:
                value_str = "(not set)"
            else:
                value_str = str(value)

            print(f"  {key} = {value_str}")
            print(f"    Source: {source}")
            print()

    return 0


def cmd_view(args: argparse.Namespace) -> int:
    """View configuration file(s).

    Args:
        args: Command-line arguments

    Returns:
        Exit code (0 = success, 1 = error)
    """
    if args.all:
        # View all config files
        config_files = _find_config_files()

        if not config_files:
            print("No configuration files found.")
            return 0

        print("Configuration Files (in precedence order):")
        print()

        for i, config_file in enumerate(config_files, 1):
            exists = config_file.exists()
            status = "✓ exists" if exists else "✗ not found"

            print(f"{i}. {config_file} ({status})")
            if exists:
                print()
                content = config_file.read_text()
                # Indent file content
                for line in content.splitlines():
                    print(f"     {line}")
            print()
    else:
        # View specific file
        if not args.path:
            print("Error: --path required when not using --all", file=sys.stderr)
            return 1

        config_file = Path(args.path)

        if not config_file.exists():
            print(
                f"Error: Configuration file not found: {config_file}", file=sys.stderr
            )
            return 1

        print(f"Configuration File: {config_file}")
        print()
        print(config_file.read_text())

    return 0


def cmd_init(args: argparse.Namespace) -> int:
    """Initialize configuration file.

    Args:
        args: Command-line arguments

    Returns:
        Exit code (0 = success, 1 = error)
    """
    if args.path:
        config_file = Path(args.path)
    else:
        # Default to ~/.jux/config
        config_file = Path.home() / ".jux" / "config"

    # Check if file exists
    if config_file.exists() and not args.force:
        print(
            f"Error: Configuration file already exists: {config_file}",
            file=sys.stderr,
        )
        print("Use --force to overwrite.", file=sys.stderr)
        return 1

    # Create parent directory if needed
    config_file.parent.mkdir(parents=True, exist_ok=True)

    # Generate config content based on template
    template_generators = {
        "minimal": _generate_minimal_template,
        "full": _generate_full_template,
        "development": _generate_development_template,
        "ci": _generate_ci_template,
        "production": _generate_production_template,
    }

    generator = template_generators.get(args.template, _generate_minimal_template)
    content = generator()

    # Write config file
    config_file.write_text(content)

    print(f"Created configuration file: {config_file}")
    print(f"Template: {args.template}")
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    """Validate configuration.

    Args:
        args: Command-line arguments

    Returns:
        Exit code (0 = success)
    """
    config = ConfigurationManager()

    # Load from environment
    config.load_from_env()

    # Load from config files (skip non-INI files)
    for config_file in _find_config_files():
        # Only load .conf and .ini files
        if config_file.suffix in [".conf", ".ini"]:
            config.load_from_file(config_file)

    # Validate
    errors = config.validate(strict=args.strict)

    if args.json:
        # JSON output
        output = {
            "valid": len(errors) == 0,
            "warnings": errors,
        }
        print(json.dumps(output, indent=2))
    else:
        # Text output
        if errors:
            print("Configuration Warnings:")
            print()
            for error in errors:
                print(f"  ⚠  {error}")
            print()
            if args.strict:
                print("Configuration has warnings but is valid.")
            else:
                print("Run with --strict to see dependency warnings.")
        else:
            print("✓ Configuration is valid.")

    return 0


def _find_config_files() -> list[Path]:
    """Find configuration files in standard locations.

    Returns:
        List of potential config file paths (in precedence order)
    """
    config_files = []

    # User-level config
    user_config = Path.home() / ".jux" / "config"
    if user_config.exists():
        config_files.append(user_config)

    # Project-level configs (only .conf and .ini for now)
    project_configs = [
        Path(".jux.conf"),
        Path("pytest.ini"),
    ]
    for config_file in project_configs:
        if config_file.exists():
            config_files.append(config_file)

    # System-level config (Linux/Unix)
    system_config = Path("/etc/jux/config")
    if system_config.exists():
        config_files.append(system_config)

    return config_files


def _generate_minimal_template() -> str:
    """Generate minimal configuration template.

    Returns:
        Configuration file content
    """
    return """[jux]
# Enable pytest-jux plugin
enabled = false

# Enable report signing
sign = false

# Storage mode: local|api|both|cache
storage_mode = local

# Enable API publishing
publish = false
"""


def _generate_full_template() -> str:
    """Generate full configuration template with all options.

    Returns:
        Configuration file content
    """
    return """[jux]
# Core Settings
# -------------

# Enable pytest-jux plugin
enabled = false

# Enable report signing (requires key_path)
sign = false

# Enable API publishing (requires api_url)
publish = false

# Storage Settings
# ----------------

# Storage mode:
#   - local: Store locally only (no API publishing)
#   - api:   Publish to API only (no local storage)
#   - both:  Store locally AND publish to API
#   - cache: Store locally, publish when API available (offline queue)
storage_mode = local

# Custom storage directory path (optional)
# storage_path = ~/.local/share/jux/reports

# Signing Settings
# ----------------

# Path to signing key (PEM format)
# key_path = ~/.jux/signing_key.pem

# Path to X.509 certificate (optional)
# cert_path = ~/.jux/signing_key.crt

# API Settings
# ------------

# API endpoint URL
# api_url = https://jux.example.com/api/v1

# API authentication key (use environment variable for security)
# api_key = your-api-key-here
# Or set via environment: JUX_API_KEY=your-api-key
"""


def _generate_development_template() -> str:
    """Generate development environment configuration template.

    Returns:
        Configuration file content optimized for development
    """
    return """[jux]
# Development Environment Configuration
# ======================================

# Core Settings
enabled = true
sign = true
publish = false

# Storage Settings
storage_mode = local
# storage_path = ~/.local/share/jux/reports

# Development Signing Settings
# Use separate development keys (NEVER use production keys in development!)
key_path = ~/.jux/dev-key.pem
cert_path = ~/.jux/dev-cert.pem

# Development Notes:
# ------------------
# 1. Generate development keys: jux-keygen --output ~/.jux/dev-key.pem --cert
# 2. Development keys should use RSA-2048 for faster signing
# 3. Self-signed certificates are acceptable for development
# 4. Never commit keys to version control
# 5. Use JUX_DEBUG=1 for verbose error messages during development
"""


def _generate_ci_template() -> str:
    """Generate CI/CD environment configuration template.

    Returns:
        Configuration file content optimized for CI/CD pipelines
    """
    return """[jux]
# CI/CD Environment Configuration
# =================================

# Core Settings
enabled = true
sign = true
publish = false  # Enable if publishing to API from CI

# Storage Settings
storage_mode = local  # Use 'api' or 'both' if publishing from CI
# storage_path = /tmp/jux-reports  # CI-specific temporary storage

# CI Signing Settings
# Use environment variables for secure key management in CI/CD
# DO NOT hardcode paths - use CI secrets/variables
# key_path = /path/from/ci/secrets/signing-key.pem
# cert_path = /path/from/ci/secrets/signing-cert.pem

# API Settings (if publishing from CI)
# api_url = https://jux.example.com/api/v1
# Use CI secrets for API key: JUX_API_KEY=<ci-secret>

# CI/CD Best Practices:
# --------------------
# 1. Store signing keys as CI secrets/encrypted variables
# 2. Use environment variables: JUX_KEY_PATH, JUX_CERT_PATH, JUX_API_KEY
# 3. Rotate keys regularly (e.g., every 90 days)
# 4. Use separate keys per environment (dev/staging/prod)
# 5. Verify signed reports: jux-verify --cert $JUX_CERT_PATH signed.xml
# 6. Archive signed reports as build artifacts
# 7. Enable signing in required CI jobs only (not for PRs from forks)
#
# Example GitHub Actions:
#   - name: Sign test reports
#     env:
#       JUX_KEY_PATH: ${{ secrets.JUX_SIGNING_KEY }}
#       JUX_CERT_PATH: ${{ secrets.JUX_SIGNING_CERT }}
#     run: |
#       pytest --junitxml=junit.xml
#       jux-sign -i junit.xml -o junit-signed.xml
#
# Example GitLab CI:
#   variables:
#     JUX_KEY_PATH: $CI_SIGNING_KEY
#     JUX_CERT_PATH: $CI_SIGNING_CERT
#   script:
#     - pytest --junitxml=junit.xml
#     - jux-sign -i junit.xml -o junit-signed.xml
"""


def _generate_production_template() -> str:
    """Generate production environment configuration template.

    Returns:
        Configuration file content optimized for production
    """
    return """[jux]
# Production Environment Configuration
# =====================================

# Core Settings
enabled = true
sign = true
publish = true  # Enable API publishing for production

# Storage Settings
storage_mode = both  # Store locally AND publish to API for redundancy
# storage_path = /var/lib/jux/reports  # Production storage path

# Production Signing Settings
# CRITICAL: Use production-grade keys with proper key management
key_path = /etc/jux/production-key.pem
cert_path = /etc/jux/production-cert.pem

# API Settings
api_url = https://jux.example.com/api/v1
# api_key = <use JUX_API_KEY environment variable>

# Production Security Requirements:
# ---------------------------------
# 1. Use RSA-4096 or ECDSA-P384 keys for production signing
# 2. Store keys with restrictive permissions (0600, root:jux)
# 3. Use CA-signed certificates (not self-signed)
# 4. Rotate keys every 90 days minimum
# 5. Use Hardware Security Module (HSM) if available
# 6. Enable audit logging for all signing operations
# 7. Monitor for signature verification failures
# 8. Implement key backup and recovery procedures
#
# Key Generation for Production:
#   jux-keygen --type rsa --bits 4096 --output /etc/jux/production-key.pem --cert \\
#     --subject "CN=Production CI/CD,O=Your Organization,C=US" --days-valid 90
#
# Key Management:
#   - Store keys in secure vault (HashiCorp Vault, AWS Secrets Manager, etc.)
#   - Use separate keys per production environment
#   - Never share keys between environments
#   - Implement automated key rotation
#   - Maintain key inventory and expiration tracking
#
# Monitoring:
#   - Alert on signature verification failures
#   - Track signing key usage and rotation dates
#   - Monitor API publishing success/failure rates
#   - Log all configuration changes
"""


def create_parser() -> argparse.ArgumentParser:
    """Create argument parser for config command.

    Returns:
        Configured ArgumentParser
    """
    epilog = """
examples:
  List all configuration options:
    jux-config list

  Show current effective configuration:
    jux-config dump

  View configuration file:
    jux-config view ~/.jux/config

  Initialize new configuration (minimal):
    jux-config init

  Initialize with full template (all options):
    jux-config init --template full

  Initialize for development environment:
    jux-config init --template development --path ~/.jux/dev-config

  Initialize for CI/CD environment:
    jux-config init --template ci --path .jux.conf

  Initialize for production environment:
    jux-config init --template production --path /etc/jux/config --force

  Validate configuration:
    jux-config validate

  Validate with strict checks:
    jux-config validate --strict

template descriptions:
  minimal      Basic configuration with essential options
  full         Complete configuration with all options and comments
  development  Development environment with local signing (RSA-2048)
  ci           CI/CD environment with security best practices and examples
  production   Production environment with security requirements (RSA-4096)

For detailed documentation, see:
  https://docs.pytest-jux.org/reference/cli/config/
"""

    parser = argparse.ArgumentParser(
        prog="jux-config",
        description="Manage pytest-jux configuration settings.\n\n"
        "View, validate, and initialize configuration files. "
        "Configuration can be stored in multiple locations with precedence: "
        "CLI args > Environment vars > User config > System config > Defaults.",
        epilog=epilog,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    subparsers = parser.add_subparsers(
        dest="command",
        help="Configuration management subcommands",
        metavar="COMMAND",
    )

    # List subcommand
    parser_list = subparsers.add_parser(
        "list",
        help="List all available configuration options with descriptions",
        description="Display complete list of configuration options, "
        "their types, defaults, and descriptions.",
    )
    parser_list.add_argument(
        "--json",
        action="store_true",
        help="Output configuration options in JSON format",
    )

    # Dump subcommand
    parser_dump = subparsers.add_parser(
        "dump",
        help="Show current effective configuration (merged from all sources)",
        description="Display the final configuration after merging all sources "
        "(CLI args, environment variables, config files, defaults).",
    )
    parser_dump.add_argument(
        "--json",
        action="store_true",
        help="Output effective configuration in JSON format",
    )

    # View subcommand
    parser_view = subparsers.add_parser(
        "view",
        help="View contents of configuration file(s)",
        description="Read and display configuration file contents. "
        "Use --all to view all configuration files in the search path.",
    )
    parser_view.add_argument(
        "path",
        nargs="?",
        help="Specific configuration file path to view (optional). "
        "If not provided, shows default user config location",
        metavar="FILE",
    )
    parser_view.add_argument(
        "--all",
        action="store_true",
        help="View all configuration files found in search path "
        "(user config, system config, etc.)",
    )

    # Init subcommand
    parser_init = subparsers.add_parser(
        "init",
        help="Create new configuration file from template",
        description="Initialize a new configuration file from environment-specific templates. "
        "Choose from minimal, full, development, CI/CD, or production templates.",
    )
    parser_init.add_argument(
        "--path",
        type=str,
        help="Configuration file path (default: ~/.jux/config). "
        "Parent directories will be created if needed",
        metavar="FILE",
    )
    parser_init.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing configuration file. "
        "Without this flag, init will fail if file already exists",
    )
    parser_init.add_argument(
        "--template",
        choices=["minimal", "full", "development", "ci", "production"],
        default="minimal",
        help="Configuration template to use: "
        "'minimal' (basic options), "
        "'full' (all options with comments), "
        "'development' (dev environment with local signing), "
        "'ci' (CI/CD with best practices and examples), "
        "'production' (production with security requirements). "
        "Default: minimal",
    )

    # Validate subcommand
    parser_validate = subparsers.add_parser(
        "validate",
        help="Validate configuration file syntax and values",
        description="Check configuration file for syntax errors, invalid values, "
        "and missing required options. Use --strict for dependency validation.",
    )
    parser_validate.add_argument(
        "--strict",
        action="store_true",
        help="Enable strict validation including dependency checks "
        "(e.g., verify key files exist, check certificate validity)",
    )
    parser_validate.add_argument(
        "--json",
        action="store_true",
        help="Output validation results in JSON format "
        "(includes success status and error details)",
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    """Main entry point for config command.

    Args:
        argv: Command-line arguments (default: sys.argv[1:])

    Returns:
        Exit code (0 = success, 1 = error, 2 = usage error)
    """
    parser = create_parser()
    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        return 2

    # Dispatch to subcommand handler
    if args.command == "list":
        return cmd_list(args)
    elif args.command == "dump":
        return cmd_dump(args)
    elif args.command == "view":
        return cmd_view(args)
    elif args.command == "init":
        return cmd_init(args)
    elif args.command == "validate":
        return cmd_validate(args)
    else:
        parser.print_help()
        return 2


if __name__ == "__main__":
    sys.exit(main())

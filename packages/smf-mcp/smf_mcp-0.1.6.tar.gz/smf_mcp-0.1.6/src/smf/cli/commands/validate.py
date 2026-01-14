import argparse
import sys
from pathlib import Path
from typing import List

import pytest


def add_parser(subparsers) -> None:
    validate_parser = subparsers.add_parser("validate", help="Validate configuration")
    validate_parser.add_argument("--config", default="smf.yaml", help="Config file path")
    validate_parser.add_argument(
        "--tests", "-t",
        action="store_true",
        help="Also run comprehensive configuration tests",
    )
    validate_parser.add_argument(
        "--verbose", "-v", action="store_true", help="Verbose output"
    )
    validate_parser.set_defaults(func=validate_command)


def validate_command(args: argparse.Namespace) -> int:
    """
    Validate SMF configuration.

    This command validates the configuration file syntax and values.
    Use --tests (-t) to also run comprehensive tests.

    Args:
        args: CLI arguments

    Returns:
        Exit code (0 = success, 1 = failure)
    """
    from smf.validation import validate_config_file
    from smf.settings import load_settings

    config_file = Path(args.config)
    if not config_file.exists():
        print(f"Error: Config file not found: {config_file}", file=sys.stderr)
        return 1

    # Step 1: Validation of the configuration file
    print("Step 1: Validating configuration file...")
    success, errors, warnings = validate_config_file(config_file)

    if errors:
        print("\nConfiguration validation failed:\n", file=sys.stderr)
        for error in errors:
            print(f"  • {error}", file=sys.stderr)
        return 1

    if warnings:
        print("\nWarnings:\n")
        for warning in warnings:
            print(f"  • {warning}")

    # Display the configuration information
    try:
        settings = load_settings(base_dir=config_file.parent, config_file=config_file)
        print("\nConfiguration is valid")
        print(f"   Server name: {settings.server_name}")
        print(f"   Transport: {settings.transport}")
        print(f"   Environment: {settings.environment}")
        print(f"   Auth provider: {settings.auth_provider}")
    except Exception as e:
        print(f"\nError loading configuration: {e}", file=sys.stderr)
        return 1

    # Step 2: Run the comprehensive configuration tests (only if --tests or -t)
    if not args.tests:
        return 0

    print("\nStep 2: Running comprehensive configuration tests...\n")

    # Get the paths of the test modules
    # The tests are in smf/testing/ (in the installed package)
    try:
        import smf.testing
        testing_dir = Path(smf.testing.__file__).parent
    except (ImportError, AttributeError):
        # Fallback: use the relative path from this file
        testing_dir = Path(__file__).parent.parent.parent / "testing"
    
    test_files = [
        testing_dir / "test_config_validation.py",
        testing_dir / "test_config_integration.py",
    ]

    # Check that the test files exist
    existing_test_files = [f for f in test_files if f.exists()]
    if not existing_test_files:
        print(
            f"Warning: No test files found in {testing_dir}", file=sys.stderr
        )
        print("   Configuration validation passed, but tests could not be run.", file=sys.stderr)
        return 0  # Return 0 because the basic validation passed

    # Prepare the pytest arguments
    pytest_args: List[str] = [str(f) for f in existing_test_files]
    if args.verbose:
        pytest_args.append("-v")

    # Run pytest
    exit_code = pytest.main(pytest_args)

    if exit_code == 0:
        print("\nAll configuration tests passed!")
        return 0
    else:
        print("\nSome configuration tests failed!", file=sys.stderr)
        return exit_code

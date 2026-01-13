#!/usr/bin/env python
"""Script to build and publish the package to PyPI."""

import os
import subprocess
import sys


def check_token() -> bool:
    """Check if UV_PUBLISH_TOKEN is set.

    Returns:
        True if token is set, False otherwise
    """
    return bool(os.environ.get("UV_PUBLISH_TOKEN"))


def run_command(command: list[str], description: str) -> None:
    """Run a shell command and handle errors.

    Args:
        command: Command to run as list of strings
        description: Description of what the command does
    """
    print(f"\n{'=' * 60}")
    print(f"{description}")
    print(f"{'=' * 60}")
    print(f"Running: {' '.join(command)}")

    result = subprocess.run(command, capture_output=False)

    if result.returncode != 0:
        print(f"\n❌ Error: {description} failed!")
        sys.exit(1)

    print(f"\n✅ {description} completed successfully!")


def main() -> None:
    """Build and publish the package."""
    print("\n" + "🚀 " * 20)
    print("FHL Bible API - Build and Publish Script")
    print("🚀 " * 20)

    # Step 1: Run tests
    run_command(
        ["uv", "run", "pytest", "--cov=fhl_bible_api"],
        "Running tests with coverage",
    )

    # Step 2: Run linter
    run_command(
        ["uv", "run", "ruff", "check", "."],
        "Running linter (ruff check)",
    )

    # Step 3: Format code
    run_command(
        ["uv", "run", "ruff", "format", "."],
        "Formatting code (ruff format)",
    )

    # Step 4: Build package
    run_command(
        ["uv", "build"],
        "Building package",
    )

    # Step 5: Prompt for publishing
    print("\n" + "=" * 60)
    print("Package built successfully!")
    print("=" * 60)
    print("\n📋 Publishing Options:")
    print("  1. Test on TestPyPI first (recommended)")
    print("  2. Publish to production PyPI")
    print("  3. Skip publishing")
    print("\n⚠️  Make sure you have set the UV_PUBLISH_TOKEN environment variable:")
    print("\n  Windows (PowerShell):")
    print("    $env:UV_PUBLISH_TOKEN = 'your-token'")
    print("\n  Linux/Mac:")
    print("    export UV_PUBLISH_TOKEN='your-token'")
    print("\n💡 Get tokens from:")
    print("  - PyPI: https://pypi.org/manage/account/token/")
    print("  - TestPyPI: https://test.pypi.org/manage/account/token/")
    print("=" * 60)

    # Check if token is set
    if not check_token():
        print("\n⚠️  Warning: UV_PUBLISH_TOKEN environment variable is not set!")
        print("Publishing will fail without a valid token.")
        proceed = input("\nContinue anyway? (yes/no): ")
        if proceed.lower() not in ["yes", "y"]:
            print("\n📦 Build complete. Publish skipped.")
            return

    response = input("\nEnter your choice (1/2/3): ").strip()

    if response == "1":
        print("\n🧪 Publishing to TestPyPI...")
        print("Make sure UV_PUBLISH_TOKEN is set to your TestPyPI token!")
        confirm = input("Continue? (yes/no): ")
        if confirm.lower() in ["yes", "y"]:
            run_command(
                ["uv", "publish", "--index", "testpypi"],
                "Publishing to TestPyPI",
            )
            print("\n✨ Package published to TestPyPI! ✨")
            print("\n📦 Test installation with:")
            print("  pip install --index-url https://test.pypi.org/simple/ \\")
            print("    --extra-index-url https://pypi.org/simple/ fhl-bible-api")
    elif response == "2":
        print("\n🚀 Publishing to production PyPI...")
        print("Make sure UV_PUBLISH_TOKEN is set to your PyPI token!")
        confirm = input("Are you sure? This cannot be undone! (yes/no): ")
        if confirm.lower() in ["yes", "y"]:
            run_command(
                ["uv", "publish"],
                "Publishing to PyPI",
            )
            print("\n✨ Package published to PyPI! ✨")
            print("\n📦 Install with:")
            print("  pip install fhl-bible-api")
    else:
        print("\n📦 Build complete. Publish skipped.")


if __name__ == "__main__":
    main()

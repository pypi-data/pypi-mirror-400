"""
AI Assess Tech CLI

Command-line interface for running assessments and verifying results.

Usage:
    aiassess assess --key hck_... --provider openai --model gpt-4
    aiassess verify <run_id>
    aiassess config --key hck_...
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Optional

from aiassess._version import __version__


def main(args: Optional[list] = None) -> int:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="aiassess",
        description="AI Assess Tech - Ethical AI Assessment Tool",
    )
    parser.add_argument(
        "-v", "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # assess command
    assess_parser = subparsers.add_parser(
        "assess",
        help="Run an ethical assessment",
    )
    assess_parser.add_argument(
        "--key",
        type=str,
        default=os.environ.get("AIASSESS_KEY"),
        help="Health Check Key (or set AIASSESS_KEY env var)",
    )
    assess_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run in dry-run mode (5 questions, mock scores)",
    )
    assess_parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON",
    )

    # verify command
    verify_parser = subparsers.add_parser(
        "verify",
        help="Verify an assessment result",
    )
    verify_parser.add_argument(
        "run_id",
        type=str,
        help="The run ID to verify",
    )
    verify_parser.add_argument(
        "--key",
        type=str,
        default=os.environ.get("AIASSESS_KEY"),
        help="Health Check Key (or set AIASSESS_KEY env var)",
    )

    # config command
    config_parser = subparsers.add_parser(
        "config",
        help="Show configuration for a Health Check Key",
    )
    config_parser.add_argument(
        "--key",
        type=str,
        default=os.environ.get("AIASSESS_KEY"),
        help="Health Check Key (or set AIASSESS_KEY env var)",
    )

    parsed = parser.parse_args(args)

    if parsed.command is None:
        parser.print_help()
        return 0

    if parsed.command == "assess":
        return cmd_assess(parsed)
    elif parsed.command == "verify":
        return cmd_verify(parsed)
    elif parsed.command == "config":
        return cmd_config(parsed)

    return 0


def cmd_assess(args: argparse.Namespace) -> int:
    """Run an assessment."""
    if not args.key:
        print("❌ Error: No Health Check Key provided", file=sys.stderr)
        print("   Use --key or set AIASSESS_KEY environment variable", file=sys.stderr)
        return 1

    try:
        from aiassess import AIAssessClient
    except ImportError as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        return 1

    print("╔════════════════════════════════════════════════════════════════╗")
    print("║  AI ASSESS TECH - Ethical AI Assessment                        ║")
    print("╚════════════════════════════════════════════════════════════════╝")
    print()

    # For CLI, we need a simple mock callback
    # In real use, users would provide their own AI integration
    def mock_callback(question: str) -> str:
        """Simple mock that always picks 'A' - for demonstration only."""
        return "A"

    print("⚠️  Note: CLI uses a mock AI callback for demonstration.")
    print("   For real assessments, use the Python SDK directly.")
    print()

    try:
        with AIAssessClient(health_check_key=args.key) as client:
            result = client.assess(
                callback=mock_callback,
                dry_run=args.dry_run,
                on_progress=lambda p: print(
                    f"  [{p.percentage:3d}%] Testing {p.dimension}..."
                ),
            )

        print()

        if args.json:
            print(result.model_dump_json(indent=2))
        else:
            status = "PASSED ✅" if result.overall_passed else "FAILED ❌"
            print(f"Result: {result.classification} ({status})")
            print()
            print("Scores:")
            print(f"  Lying:    {result.scores.lying:.2f}/10")
            print(f"  Cheating: {result.scores.cheating:.2f}/10")
            print(f"  Stealing: {result.scores.stealing:.2f}/10")
            print(f"  Harm:     {result.scores.harm:.2f}/10")
            print()
            print(f"Verify at: {result.verify_url}")

        return 0 if result.overall_passed else 1

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        return 1


def cmd_verify(args: argparse.Namespace) -> int:
    """Verify an assessment result."""
    if not args.key:
        print("❌ Error: No Health Check Key provided", file=sys.stderr)
        return 1

    try:
        from aiassess import AIAssessClient
    except ImportError as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        return 1

    try:
        with AIAssessClient(health_check_key=args.key) as client:
            result = client.verify(args.run_id)

        print(json.dumps(result, indent=2))
        return 0

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        return 1


def cmd_config(args: argparse.Namespace) -> int:
    """Show configuration for a key."""
    if not args.key:
        print("❌ Error: No Health Check Key provided", file=sys.stderr)
        return 1

    try:
        from aiassess import AIAssessClient
    except ImportError as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        return 1

    try:
        with AIAssessClient(health_check_key=args.key) as client:
            config = client.get_config()

        print(f"Test Mode:     {config.test_mode}")
        print(f"Framework:     {config.framework_id}")
        print(f"Organization:  {config.organization_name}")
        print(f"Key Name:      {config.key_name}")
        print(f"Questions:     {len(config.questions)}")
        print()
        print("Thresholds:")
        print(f"  Lying:    {config.thresholds.lying}")
        print(f"  Cheating: {config.thresholds.cheating}")
        print(f"  Stealing: {config.thresholds.stealing}")
        print(f"  Harm:     {config.thresholds.harm}")

        return 0

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())


"""Command-line interface for onshnap.

Usage:
    onshnap <directory>

Where <directory> contains a config.json with the Onshape document URL.
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

import colorlogging

from .core import run_export


def setup_logging(verbose: bool = False) -> None:
    """Configure logging for the CLI using colorlogging."""
    level = logging.DEBUG if verbose else logging.INFO

    colorlogging.configure(level=level)

    # Reduce noise from requests/urllib3
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)


def main() -> int:
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        prog="onshnap",
        description="Export Onshape assemblies to frozen-snapshot URDF files.",
        epilog=(
            "Environment variables:\n"
            "  ONSHAPE_ACCESS_KEY  Your Onshape API access key\n"
            "  ONSHAPE_SECRET_KEY  Your Onshape API secret key\n\n"
            "The target directory must contain a config.json file with:\n"
            '  {"url": "https://cad.onshape.com/documents/..."}'
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "directory",
        type=Path,
        help="Directory containing config.json with the Onshape document URL",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose (debug) logging",
    )

    args = parser.parse_args()

    # Setup logging
    setup_logging(verbose=args.verbose)

    logger = logging.getLogger(__name__)

    # Validate directory
    target_dir: Path = args.directory
    if not target_dir.is_dir():
        logger.error("Error: '%s' is not a directory", target_dir)
        return 1

    config_path = target_dir / "config.json"
    if not config_path.exists():
        logger.error("Error: config.json not found in '%s'", target_dir)
        return 1

    # Run export
    try:
        urdf_path = run_export(target_dir)
        print(f"\n✓ Successfully exported URDF to: {urdf_path}")
        return 0

    except ValueError as e:
        logger.error("Configuration error: %s", e)
        return 1

    except Exception as e:
        logger.exception("Export failed: %s", e)
        return 1


if __name__ == "__main__":
    sys.exit(main())

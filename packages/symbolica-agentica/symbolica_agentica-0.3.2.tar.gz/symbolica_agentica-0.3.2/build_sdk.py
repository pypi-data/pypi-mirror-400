#!/usr/bin/env python3
"""
Build the Agentica Python SDK.

This is a convenience script that wraps `uv build` for building both agentica-internal and the SDK with consistent versioning. It does two things:

1. Builds agentica-internal (from common/)
2. Builds the SDK itself

Both packages get their version from git tags via setuptools-scm. The script
uses get-version.sh to determine the version and passes it to the build via
SETUPTOOLS_SCM_PRETEND_VERSION environment variable.

This script is NOT required for building - you can also build manually:

    # To build agentica-internal
    cd common && uv build

    # To build the SDK
    cd ustomer_sdk/python
    uv build

Note that in order to install the locally built SDK, you need to install the agentica-internal wheel first or provide it along with the SDK wheel.
Or, as a second option, it's possible to specify agentica-internal path to common/ under [tool.uv.sources] in pyproject.toml and do uv sync before installing.

The script just provides convenience for:
- Building both packages in one command
- Consistent version handling across both packages
- Different version modes (dev, prerelease, release)

Version Modes:
    prev (default): Development version with git hash (0.3.1.dev25+abc123)
    dev:            Development version without hash (0.3.1.dev25)
    prerelease:     Release candidate (0.3.1-rc, normalized to 0.3.1rc0 by pip)
    release:        Clean release version (0.3.1)

Examples:
    ./build_sdk.py                          # Default dev build
    ./build_sdk.py --version-mode release   # Release build
    ./build_sdk.py --version 1.2.3          # Manual version for testing
    ./build_sdk.py --skip-internal          # Only build SDK
"""

import argparse
import logging
import subprocess
import sys
from pathlib import Path

logger = logging.getLogger(__name__)

# Default paths (relative to this script's location)
DEFAULT_COMMON_DIR = Path("../../common")
DEFAULT_SDK_DIR = Path(".")


def run_cmd(cmd: list[str], cwd: Path, env: dict | None = None) -> None:
    """Run a command and raise on failure."""
    logger.info(f"Running: {' '.join(cmd)} (in {cwd})")
    result = subprocess.run(cmd, cwd=cwd, env=env)
    if result.returncode != 0:
        raise RuntimeError(f"Command failed: {' '.join(cmd)}")


def get_version_from_script(script_dir: Path, mode: str) -> str:
    """
    Get version from get-version.sh.

    Mode mapping:
      prev       -> get-version.sh prev python       -> 0.3.1.dev25+abc123
      dev        -> get-version.sh dev python        -> 0.3.1.dev25
      prerelease -> get-version.sh prod python rc    -> 0.3.1-rc
      release    -> get-version.sh prod python release -> 0.3.1
    """
    get_version_script = script_dir / "get-version.sh"

    # Map our friendly modes to get-version.sh arguments
    mode_mapping = {
        "prev": ["prev", "python"],
        "dev": ["dev", "python"],
        "prerelease": ["prod", "python", "rc"],
        "release": ["prod", "python", "release"],
    }

    if mode not in mode_mapping:
        raise ValueError(f"Unknown mode: {mode}. Must be one of: {list(mode_mapping.keys())}")

    cmd = [str(get_version_script)] + mode_mapping[mode]

    result = subprocess.run(cmd, cwd=script_dir, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Failed to get version: {result.stderr}")

    return result.stdout.strip()


def build_package(pkg_dir: Path, version: str | None = None) -> Path:
    """Build a package and return the wheel path."""
    env = None
    if version:
        env = {**subprocess.os.environ, "SETUPTOOLS_SCM_PRETEND_VERSION": version}
        logger.info(f"Using version: {version}")

    # Clean previous builds
    dist_dir = pkg_dir / "dist"
    if dist_dir.exists():
        import shutil

        shutil.rmtree(dist_dir)

    run_cmd(["uv", "build"], cwd=pkg_dir, env=env)

    wheels = list(dist_dir.glob("*.whl"))
    if len(wheels) != 1:
        raise RuntimeError(f"Expected 1 wheel in {dist_dir}, got {len(wheels)}")

    return wheels[0]


def install_wheel(wheel: Path, target_dir: Path) -> None:
    """Install a wheel into the target directory's venv."""
    run_cmd(["uv", "pip", "install", str(wheel)], cwd=target_dir)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build the Agentica SDK",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--common-dir",
        type=Path,
        default=DEFAULT_COMMON_DIR,
        help="Path to agentica-internal (common) directory",
    )
    parser.add_argument(
        "--sdk-dir",
        type=Path,
        default=DEFAULT_SDK_DIR,
        help="Path to the SDK directory",
    )

    parser.add_argument(
        "--version",
        type=str,
        help="Manually specify version (e.g., 0.3.1 for testing)",
    )
    parser.add_argument(
        "--version-mode",
        choices=["prev", "dev", "prerelease", "release"],
        default="prev",
        help=(
            "Version mode (ignored if --version is set). "
            "prev: 0.3.1.dev25+abc123, "
            "dev: 0.3.1.dev25, "
            "prerelease: 0.3.1-rc, "
            "release: 0.3.1"
        ),
    )
    parser.add_argument(
        "--skip-internal",
        action="store_true",
        help="Skip building agentica-internal (only build SDK)",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging",
    )

    return parser.parse_args()


def main() -> int:
    args = parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )

    script_dir = Path(__file__).parent.resolve()
    common_dir = (script_dir / args.common_dir).resolve()
    sdk_dir = (script_dir / args.sdk_dir).resolve()

    logger.info(f"Common dir: {common_dir}")
    logger.info(f"SDK dir: {sdk_dir}")

    # Determine version (priority: env var > --version flag > get-version.sh)
    version = None
    env_version = subprocess.os.environ.get("SETUPTOOLS_SCM_PRETEND_VERSION")
    if env_version:
        version = env_version
        logger.info(f"Using version from SETUPTOOLS_SCM_PRETEND_VERSION: {version}")
    elif args.version:
        # Manual version override
        version = args.version
        logger.info(f"Using manually specified version: {version}")
    else:
        # Get version from get-version.sh
        try:
            version = get_version_from_script(script_dir, args.version_mode)
            logger.info(f"Version from get-version.sh ({args.version_mode}): {version}")
        except Exception as e:
            logger.warning(f"Could not get version from get-version.sh: {e}")
            logger.info("Will rely on setuptools-scm to determine version from git")

    # Step 1: Build agentica-internal (unless skipped)
    internal_wheel = None
    if not args.skip_internal:
        logger.info("=" * 50)
        logger.info("Building agentica-internal...")
        logger.info("=" * 50)

        internal_wheel = build_package(common_dir, version)
        logger.info(f"Built: {internal_wheel}")
    else:
        logger.info("Skipping agentica-internal build (--skip-internal)")

    # Step 2: Build the SDK
    logger.info("=" * 50)
    logger.info("Building SDK...")
    logger.info("=" * 50)

    sdk_wheel = build_package(sdk_dir, version)
    logger.info(f"Built: {sdk_wheel}")

    logger.info("=" * 50)
    logger.info("Build complete!")
    if internal_wheel:
        logger.info(f"Internal wheel: {internal_wheel}")
    logger.info(f"SDK wheel: {sdk_wheel}")
    logger.info("=" * 50)

    return 0


if __name__ == "__main__":
    sys.exit(main())

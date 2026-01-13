# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Maurice Garcia

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from getpass import getpass
from pathlib import Path


DIST_DIR = Path("dist")
PYPI_TOKEN_ENV = "PYPI_API_TOKEN"


class PublishTool:
    """Publish helper for PyPNM-CMTS package uploads."""

    @staticmethod
    def _build_parser() -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(description="Publish PyPNM-CMTS distributions to PyPI.")
        parser.add_argument(
            "--repository",
            choices=["pypi"],
            default="pypi",
            help="Target repository name for twine.",
        )
        parser.add_argument("--skip-build", action="store_true", help="Skip building distributions.")
        parser.add_argument("--skip-check", action="store_true", help="Skip twine check.")
        parser.add_argument("--dry-run", action="store_true", help="Skip twine upload.")
        parser.add_argument("--clean", action="store_true", help="Remove dist/ before building.")
        return parser

    @staticmethod
    def _collect_artifacts() -> list[Path]:
        artifacts = sorted(path for path in DIST_DIR.glob("*") if path.is_file())
        if not artifacts:
            raise RuntimeError(f"No artifacts found in {DIST_DIR}.")
        return artifacts

    @staticmethod
    def _resolve_token() -> str:
        token = os.environ.get(PYPI_TOKEN_ENV, "").strip()
        if token != "":
            return token
        return getpass("PyPI token: ")

    @staticmethod
    def _run(cmd: list[str], env: dict[str, str] | None = None) -> None:
        subprocess.run(cmd, check=True, cwd=Path.cwd(), env=env)

    @classmethod
    def run(cls, options: argparse.Namespace) -> int:
        if options.clean and DIST_DIR.exists():
            shutil.rmtree(DIST_DIR, ignore_errors=True)

        if not options.skip_build:
            cls._run([sys.executable, "-m", "build"])

        artifacts = cls._collect_artifacts()

        if not options.skip_check:
            check_cmd = [sys.executable, "-m", "twine", "check"]
            check_cmd.extend([str(path) for path in artifacts])
            cls._run(check_cmd)

        if options.dry_run:
            print("Dry-run enabled; skipping twine upload.")
            return 0

        token = cls._resolve_token().strip()
        if token == "":
            raise RuntimeError("PyPI token is required for upload.")

        env = dict(os.environ)
        env["TWINE_USERNAME"] = "__token__"
        env["TWINE_PASSWORD"] = token

        upload_cmd = [sys.executable, "-m", "twine", "upload", "--repository", options.repository]
        upload_cmd.extend([str(path) for path in artifacts])
        cls._run(upload_cmd, env=env)
        return 0


def main() -> int:
    parser = PublishTool._build_parser()
    options = parser.parse_args()
    try:
        return PublishTool.run(options)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

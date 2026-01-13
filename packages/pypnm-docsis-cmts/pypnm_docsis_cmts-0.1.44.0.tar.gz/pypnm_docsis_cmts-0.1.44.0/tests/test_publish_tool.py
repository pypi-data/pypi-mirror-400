# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Maurice Garcia

from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest

from pypnm_cmts.tools.publish_tool import PublishTool


class _RunCapture:
    def __init__(self) -> None:
        self.commands: list[list[str]] = []
        self.envs: list[dict[str, str] | None] = []

    def __call__(
        self,
        cmd: list[str],
        check: bool = False,
        cwd: Path | None = None,
        env: dict[str, str] | None = None,
    ) -> subprocess.CompletedProcess[str]:
        _ = check
        _ = cwd
        self.commands.append(cmd)
        self.envs.append(env)
        return subprocess.CompletedProcess(cmd, 0, stdout="", stderr="")


def _make_artifact(tmp_path: Path) -> None:
    dist_dir = tmp_path / "dist"
    dist_dir.mkdir(parents=True, exist_ok=True)
    (dist_dir / "pypnm_docsis_cmts-0.1.0.0.tar.gz").write_text("stub", encoding="utf-8")


@pytest.mark.unit
def test_publish_tool_uses_env_token(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.chdir(tmp_path)
    _make_artifact(tmp_path)
    monkeypatch.setenv("PYPI_API_TOKEN", "token-value")

    capture = _RunCapture()
    monkeypatch.setattr(subprocess, "run", capture)

    parser = PublishTool._build_parser()
    options = parser.parse_args(["--skip-build", "--skip-check"])
    assert PublishTool.run(options) == 0

    assert any("twine" in cmd for cmd in capture.commands)
    assert capture.envs
    upload_env = capture.envs[-1]
    assert upload_env is not None
    assert upload_env.get("TWINE_USERNAME") == "__token__"
    assert upload_env.get("TWINE_PASSWORD") == "token-value"


@pytest.mark.unit
def test_publish_tool_dry_run_skips_upload(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.chdir(tmp_path)
    _make_artifact(tmp_path)

    capture = _RunCapture()
    monkeypatch.setattr(subprocess, "run", capture)

    parser = PublishTool._build_parser()
    options = parser.parse_args(["--skip-build", "--skip-check", "--dry-run"])
    assert PublishTool.run(options) == 0

    assert all("upload" not in cmd for cmd in capture.commands)


@pytest.mark.unit
def test_publish_tool_prompts_for_token(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.chdir(tmp_path)
    _make_artifact(tmp_path)
    monkeypatch.delenv("PYPI_API_TOKEN", raising=False)

    capture = _RunCapture()
    monkeypatch.setattr(subprocess, "run", capture)
    monkeypatch.setattr("pypnm_cmts.tools.publish_tool.getpass", lambda _prompt: "prompt-token")

    parser = PublishTool._build_parser()
    options = parser.parse_args(["--skip-build", "--skip-check"])
    assert PublishTool.run(options) == 0

    assert capture.envs
    upload_env = capture.envs[-1]
    assert upload_env is not None
    assert upload_env.get("TWINE_PASSWORD") == "prompt-token"


@pytest.mark.unit
def test_publish_tool_build_and_check_run(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.chdir(tmp_path)
    _make_artifact(tmp_path)

    capture = _RunCapture()
    monkeypatch.setattr(subprocess, "run", capture)

    parser = PublishTool._build_parser()
    options = parser.parse_args(["--dry-run"])
    assert PublishTool.run(options) == 0

    joined = [" ".join(cmd) for cmd in capture.commands]
    assert any("-m build" in cmd for cmd in joined)
    assert any("-m twine check" in cmd for cmd in joined)
    assert all("-m twine upload" not in cmd for cmd in joined)

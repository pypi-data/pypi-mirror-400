"""Tests for airops CLI."""

from __future__ import annotations

from pathlib import Path

import pytest

from airops.cli import main
from airops.cli.init import sanitize_name


class TestSanitizeName:
    """Tests for name sanitization."""

    def test_simple_name(self) -> None:
        assert sanitize_name("mytool") == "mytool"

    def test_hyphenated_name(self) -> None:
        assert sanitize_name("my-tool") == "my_tool"

    def test_spaces(self) -> None:
        assert sanitize_name("my tool") == "my_tool"

    def test_mixed_case(self) -> None:
        assert sanitize_name("MyTool") == "mytool"

    def test_starts_with_digit(self) -> None:
        assert sanitize_name("123tool") == "tool_123tool"

    def test_special_characters(self) -> None:
        assert sanitize_name("my@tool!") == "mytool"

    def test_empty_string(self) -> None:
        assert sanitize_name("") == "my_tool"


class TestMainCli:
    """Tests for main CLI entry point."""

    def test_no_args_prints_help(self, capsys: pytest.CaptureFixture[str]) -> None:
        result = main([])
        assert result == 0
        captured = capsys.readouterr()
        assert "usage:" in captured.out.lower()

    def test_version_flag(self) -> None:
        with pytest.raises(SystemExit) as exc:
            main(["--version"])
        assert exc.value.code == 0

    def test_init_help(self) -> None:
        with pytest.raises(SystemExit) as exc:
            main(["init", "--help"])
        assert exc.value.code == 0


class TestInitCommand:
    """Tests for 'airops init' command."""

    def test_init_creates_files(self, tmp_path: Path) -> None:
        """Init creates all expected files."""
        result = main(["init", str(tmp_path)])
        assert result == 0

        assert (tmp_path / "tool.py").exists()
        assert (tmp_path / "Dockerfile").exists()
        assert (tmp_path / ".dockerignore").exists()
        assert (tmp_path / ".env.example").exists()
        assert (tmp_path / "pyproject.toml").exists()
        assert (tmp_path / "README.md").exists()
        assert (tmp_path / "AGENTS.md").exists()
        assert (tmp_path / "CLAUDE.md").exists()
        assert (tmp_path / "tests" / "__init__.py").exists()
        assert (tmp_path / "tests" / "test_tool.py").exists()

    def test_init_uses_directory_name(self, tmp_path: Path) -> None:
        """Init derives tool name from directory."""
        project_dir = tmp_path / "my-cool-tool"
        project_dir.mkdir()

        result = main(["init", str(project_dir)])
        assert result == 0

        content = (project_dir / "tool.py").read_text()
        assert 'name="my_cool_tool"' in content

    def test_init_uses_custom_name(self, tmp_path: Path) -> None:
        """Init uses --name argument."""
        result = main(["init", str(tmp_path), "--name", "custom-name"])
        assert result == 0

        content = (tmp_path / "tool.py").read_text()
        assert 'name="custom_name"' in content

    def test_init_creates_directory(self, tmp_path: Path) -> None:
        """Init creates target directory if it doesn't exist."""
        new_dir = tmp_path / "new_project"
        assert not new_dir.exists()

        result = main(["init", str(new_dir)])
        assert result == 0
        assert new_dir.exists()

    def test_init_refuses_overwrite_without_force(self, tmp_path: Path) -> None:
        """Init refuses to overwrite existing files."""
        (tmp_path / "tool.py").write_text("existing content")

        result = main(["init", str(tmp_path)])
        assert result == 1

        assert (tmp_path / "tool.py").read_text() == "existing content"

    def test_init_overwrites_with_force(self, tmp_path: Path) -> None:
        """Init overwrites files with --force."""
        (tmp_path / "tool.py").write_text("existing content")

        result = main(["init", str(tmp_path), "--force"])
        assert result == 0

        content = (tmp_path / "tool.py").read_text()
        assert "existing content" not in content
        assert "from airops import Tool" in content

    def test_init_current_directory(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Init works in current directory with no path argument."""
        monkeypatch.chdir(tmp_path)

        result = main(["init"])
        assert result == 0
        assert (tmp_path / "tool.py").exists()

    def test_init_fails_on_file_path(self, tmp_path: Path) -> None:
        """Init fails if path is a file, not a directory."""
        file_path = tmp_path / "somefile.txt"
        file_path.write_text("I am a file")

        result = main(["init", str(file_path)])
        assert result == 1

    def test_generated_tool_is_valid_python(self, tmp_path: Path) -> None:
        """Generated tool.py is valid Python syntax."""
        result = main(["init", str(tmp_path)])
        assert result == 0

        content = (tmp_path / "tool.py").read_text()
        compile(content, "tool.py", "exec")

    def test_generated_test_is_valid_python(self, tmp_path: Path) -> None:
        """Generated test file is valid Python syntax."""
        result = main(["init", str(tmp_path)])
        assert result == 0

        content = (tmp_path / "tests" / "test_tool.py").read_text()
        compile(content, "test_tool.py", "exec")


class TestRunCommand:
    """Tests for 'airops run' command."""

    def test_run_help(self) -> None:
        """Run --help works."""
        with pytest.raises(SystemExit) as exc:
            main(["run", "--help"])
        assert exc.value.code == 0

    def test_run_fails_without_dockerfile(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Run fails if no Dockerfile exists."""
        monkeypatch.chdir(tmp_path)

        result = main(["run"])
        assert result == 1

    def test_run_fails_without_tool_py(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Run fails if no tool.py exists."""
        monkeypatch.chdir(tmp_path)
        (tmp_path / "Dockerfile").write_text("FROM python:3.13")

        result = main(["run"])
        assert result == 1

    def test_run_fails_without_env(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Run fails if no .env exists."""
        monkeypatch.chdir(tmp_path)
        (tmp_path / "Dockerfile").write_text("FROM python:3.13")
        (tmp_path / "tool.py").write_text("# tool")

        result = main(["run"])
        assert result == 1

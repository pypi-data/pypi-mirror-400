import subprocess
from unittest.mock import MagicMock, patch

import pytest

from buvis.pybase.adapters.poetry.poetry import PoetryAdapter


@pytest.fixture
def mock_subprocess_run():
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = subprocess.CompletedProcess(args=[], returncode=0)
        yield mock_run


@pytest.fixture
def tmp_project(tmp_path):
    """Create a temporary project structure."""
    scripts_root = tmp_path / "scripts"
    scripts_root.mkdir()
    bin_dir = scripts_root / "bin"
    bin_dir.mkdir()
    src_dir = scripts_root / "src"
    src_dir.mkdir()
    return scripts_root


class TestRunScript:
    def test_run_script_with_poetry_project(self, mock_subprocess_run, tmp_project):
        """When project dir exists with pyproject.toml, use poetry run."""
        pkg_name = "my_script"
        project_dir = tmp_project / "src" / pkg_name
        project_dir.mkdir()
        (project_dir / "pyproject.toml").write_text("[tool.poetry]")

        script_path = tmp_project / "bin" / "my-script"
        script_path.write_text("#!/usr/bin/env python")

        with pytest.raises(SystemExit) as exc_info:
            PoetryAdapter.run_script(str(script_path), ["arg1", "arg2"])

        assert exc_info.value.code == 0
        mock_subprocess_run.assert_called_once_with(
            ["poetry", "run", "python", "-m", "my_script.cli", "arg1", "arg2"],
            cwd=project_dir,
            check=False,
        )

    def test_run_script_without_poetry_project(self, tmp_project):
        """When project dir doesn't exist, use importlib."""
        script_path = tmp_project / "bin" / "my-script"
        script_path.write_text("#!/usr/bin/env python")

        mock_module = MagicMock()
        with patch("importlib.import_module", return_value=mock_module) as mock_import:
            PoetryAdapter.run_script(str(script_path), ["arg1"])

        mock_import.assert_called_once_with("my_script.cli")
        mock_module.main.assert_called_once_with(["arg1"])


class TestUpdateScript:
    def test_update_script_with_project(self, mock_subprocess_run, tmp_project):
        """When project exists, call _update_poetry_project."""
        pkg_name = "my_script"
        project_dir = tmp_project / "src" / pkg_name
        project_dir.mkdir()
        (project_dir / "pyproject.toml").write_text("[tool.poetry]")
        lock_file = project_dir / "poetry.lock"
        lock_file.write_text("lock content")

        script_path = tmp_project / "bin" / "my-script"
        script_path.write_text("#!/usr/bin/env python")

        PoetryAdapter.update_script(str(script_path))

        # Lock file should be deleted
        assert not lock_file.exists()
        # poetry lock and install should be called
        assert mock_subprocess_run.call_count == 2

    def test_update_script_no_project(self, mock_subprocess_run, tmp_project):
        """When project doesn't exist, do nothing."""
        script_path = tmp_project / "bin" / "my-script"
        script_path.write_text("#!/usr/bin/env python")

        PoetryAdapter.update_script(str(script_path))

        mock_subprocess_run.assert_not_called()


class TestUpdatePoetryProject:
    def test_deletes_lock_and_runs_poetry(self, mock_subprocess_run, tmp_path):
        """Should delete lock file and run poetry lock + install."""
        project_dir = tmp_path / "project"
        project_dir.mkdir()
        lock_file = project_dir / "poetry.lock"
        lock_file.write_text("old lock")

        PoetryAdapter._update_poetry_project(project_dir)

        assert not lock_file.exists()
        calls = mock_subprocess_run.call_args_list
        assert len(calls) == 2
        assert calls[0][0][0] == ["poetry", "lock"]
        assert calls[0][1]["cwd"] == project_dir
        assert calls[1][0][0] == ["poetry", "install"]
        assert calls[1][1]["cwd"] == project_dir

    def test_handles_no_lock_file(self, mock_subprocess_run, tmp_path):
        """Should work when no lock file exists."""
        project_dir = tmp_path / "project"
        project_dir.mkdir()

        PoetryAdapter._update_poetry_project(project_dir)

        assert mock_subprocess_run.call_count == 2

    def test_handles_poetry_error(self, tmp_path):
        """Should catch CalledProcessError and continue."""
        project_dir = tmp_path / "project"
        project_dir.mkdir()

        with patch(
            "subprocess.run", side_effect=subprocess.CalledProcessError(1, "poetry")
        ):
            # Should not raise
            PoetryAdapter._update_poetry_project(project_dir)


class TestContainsPoetryAdapter:
    def test_file_with_import(self, tmp_path):
        """Should return True when file contains the import."""
        file_path = tmp_path / "script.py"
        file_path.write_text(
            "from buvis.pybase.adapters import PoetryAdapter\nPoetryAdapter.run_script()"
        )

        assert PoetryAdapter._contains_poetry_adapter(file_path) is True

    def test_file_without_import(self, tmp_path):
        """Should return False when file doesn't contain the import."""
        file_path = tmp_path / "script.py"
        file_path.write_text("print('hello')")

        assert PoetryAdapter._contains_poetry_adapter(file_path) is False

    def test_binary_file(self, tmp_path):
        """Should return False for binary files."""
        file_path = tmp_path / "binary"
        file_path.write_bytes(b"\x00\x01\x02\xff\xfe")

        assert PoetryAdapter._contains_poetry_adapter(file_path) is False


class TestUpdateAllScripts:
    def test_updates_scripts_with_adapter(self, mock_subprocess_run, tmp_project):
        """Should update scripts that use PoetryAdapter."""
        # Create a script that uses PoetryAdapter
        script = tmp_project / "bin" / "my-script"
        script.write_text("from buvis.pybase.adapters import PoetryAdapter\n")

        # Create corresponding project
        pkg_name = "my_script"
        project_dir = tmp_project / "src" / pkg_name
        project_dir.mkdir()
        (project_dir / "pyproject.toml").write_text("[tool.poetry]")

        PoetryAdapter.update_all_scripts(tmp_project)

        # Should have called poetry lock and install
        assert mock_subprocess_run.call_count >= 2

    def test_skips_scripts_without_adapter(self, mock_subprocess_run, tmp_project):
        """Should skip scripts that don't use PoetryAdapter."""
        script = tmp_project / "bin" / "other-script"
        script.write_text("print('hello')\n")

        PoetryAdapter.update_all_scripts(tmp_project)

        # No project to update, so no calls
        mock_subprocess_run.assert_not_called()

    def test_updates_all_src_projects(self, mock_subprocess_run, tmp_project):
        """Should update all projects in src/ directory."""
        # Create multiple projects
        for name in ["project_a", "project_b"]:
            project_dir = tmp_project / "src" / name
            project_dir.mkdir()
            (project_dir / "pyproject.toml").write_text("[tool.poetry]")

        PoetryAdapter.update_all_scripts(tmp_project)

        # Each project should have lock + install = 2 calls each
        assert mock_subprocess_run.call_count == 4

"""Tests for CLI entry point."""

from pathlib import Path

import pytest
from click.testing import CliRunner

from fabric_playlists.cli import main
from fabric_playlists.config import AppConfig


@pytest.fixture
def runner() -> CliRunner:
    """Return a Click CliRunner instance for testing."""
    return CliRunner()


class TestVersionCommand:
    """Version command tests."""

    def test_version_output(self, runner: CliRunner) -> None:
        """Version command prints the installed version and exits 0."""
        result = runner.invoke(main, ["version"])
        assert result.exit_code == 0
        assert "0.1.0" in result.output


class TestInitCommand:
    """Init command tests."""

    def test_init_creates_config(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        runner: CliRunner,
    ) -> None:
        """Init --force creates config and prints confirmation."""
        target = tmp_path / "config.toml"
        monkeypatch.setattr("fabric_playlists.cli.get_config_path", lambda: target)
        monkeypatch.setattr(
            "fabric_playlists.cli.init_config",
            lambda path=None: AppConfig(source="/test/src", dest="/test/dst"),
        )

        result = runner.invoke(main, ["init", "--force"])
        assert result.exit_code == 0
        assert "Config created" in result.output


class TestListCommand:
    """List command tests."""

    def test_list_no_playlists(self, runner: CliRunner) -> None:
        """List with nonexistent dest shows 'No playlists' message."""
        result = runner.invoke(main, ["list", "--dest", "/nonexistent"])
        assert result.exit_code == 0
        assert "No playlists" in result.output


class TestGenerateCommand:
    """Generate command tests."""

    def test_generate_creates_playlists(
        self, runner: CliRunner, temp_music_dir: Path, tmp_path: Path
    ) -> None:
        """Generate scans source, creates M3U files, skips presents/empty dirs."""
        dest = tmp_path / "output"
        result = runner.invoke(
            main,
            ["generate", "--source", str(temp_music_dir), "--dest", str(dest)],
        )

        assert result.exit_code == 0, f"CLI failed: {result.output}"
        # Check expected playlists were created
        m3u_files = sorted(dest.glob("*.m3u"))
        m3u_names = {f.stem for f in m3u_files}
        assert "FABRICLIVE_72" in m3u_names, f"Got: {m3u_names}"
        assert "fabric_100" in m3u_names, f"Got: {m3u_names}"
        # Presents dir should not produce a playlist
        assert not any("presents" in name.lower() for name in m3u_names)
        # EmptyAlbum should not produce a playlist
        assert "EmptyAlbum" not in m3u_names

    def test_generate_source_not_found(self, runner: CliRunner) -> None:
        """Generate with nonexistent source exits non-zero."""
        result = runner.invoke(
            main,
            ["generate", "--source", "/nonexistent/source/dir"],
        )
        assert result.exit_code != 0


class TestVerboseFlag:
    """Verbose flag tests."""

    def test_verbose_sets_debug(self, runner: CliRunner) -> None:
        """--verbose flag is accepted without error on a read-only command."""
        result = runner.invoke(main, ["--verbose", "version"])
        assert result.exit_code == 0
        assert "0.1.0" in result.output

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


class TestOverwriteFlag:
    """Tests for the --overwrite flag on generate."""

    def test_skips_existing_without_overwrite(self, runner, temp_music_dir, tmp_path):
        dest = tmp_path / "playlists"
        # First run
        runner.invoke(main, ["generate", "--source", str(temp_music_dir), "--dest", str(dest)])
        # Second run without --overwrite should skip
        result = runner.invoke(main, [
            "generate", "--source", str(temp_music_dir), "--dest", str(dest),
        ])
        assert result.exit_code == 0
        assert "Skipping" in result.output or "Skipped" in result.output

    def test_overwrites_with_flag(self, runner, temp_music_dir, tmp_path):
        dest = tmp_path / "playlists"
        runner.invoke(main, ["generate", "--source", str(temp_music_dir), "--dest", str(dest)])
        pl_path = dest / "FABRICLIVE_72.m3u"
        assert pl_path.exists()
        # Now overwrite
        result = runner.invoke(main, [
            "generate", "--source", str(temp_music_dir), "--dest", str(dest),
            "--overwrite",
        ])
        assert result.exit_code == 0
        assert "Skipped" not in result.output
        assert "Skipping" not in result.output
        # File still exists and was re-written (same content here, but write happened)
        assert pl_path.exists()

    def test_overwrites_dir_with_spaces(self, runner, temp_music_dir, tmp_path):
        """Verifies overwrite works when directory names contain spaces."""
        dest = tmp_path / "playlists"
        runner.invoke(main, ["generate", "--source", str(temp_music_dir), "--dest", str(dest)])
        pl_path = dest / "FABRICLIVE 95 - Test.m3u"
        assert pl_path.exists()
        # Second run without --overwrite skips
        result = runner.invoke(main, [
            "generate", "--source", str(temp_music_dir), "--dest", str(dest),
        ])
        assert "Skipping" in result.output or "Skipped" in result.output
        # With --overwrite, it writes
        result = runner.invoke(main, [
            "generate", "--source", str(temp_music_dir), "--dest", str(dest),
            "--overwrite",
        ])
        assert result.exit_code == 0
        assert "Skipping" not in result.output
        assert pl_path.exists()


class TestContinuousFile:
    """Continuous mix file overrides all other files."""

    def test_continuous_file_in_playlist(self, runner, temp_music_dir, tmp_path):
        dest = tmp_path / "playlists"
        runner.invoke(main, ["generate", "--source", str(temp_music_dir), "--dest", str(dest)])
        result = runner.invoke(main, ["info", "FABRICLIVE_CONT", "--dest", str(dest)])
        assert result.exit_code == 0
        assert "continuous.mp3" in result.output
        assert "01 - Continuous Mix.flac" in result.output
        assert "Tracks: 2" in result.output
        assert "01 - Intro.flac" not in result.output


class TestVerboseFlag:
    """Verbose flag tests."""

    def test_verbose_sets_debug(self, runner: CliRunner) -> None:
        """--verbose flag is accepted without error on a read-only command."""
        result = runner.invoke(main, ["--verbose", "version"])
        assert result.exit_code == 0
        assert "0.1.0" in result.output


class TestInfoCommand:
    def test_shows_playlist_info(self, runner, temp_music_dir, tmp_path):
        dest = tmp_path / "playlists"
        runner.invoke(main, ["generate", "--source", str(temp_music_dir), "--dest", str(dest)])
        result = runner.invoke(main, ["info", "FABRICLIVE_72", "--dest", str(dest)])
        assert result.exit_code == 0
        assert "FABRICLIVE_72" in result.output
        assert "tracks" in result.output.lower()

    def test_info_missing_playlist(self, runner, tmp_path):
        dest = tmp_path / "playlists"
        result = runner.invoke(main, ["info", "nonexistent", "--dest", str(dest)])
        assert result.exit_code != 0


class TestValidateCommand:
    def test_validate_passes(self, runner, temp_music_dir, tmp_path):
        dest = tmp_path / "playlists"
        runner.invoke(main, ["generate", "--source", str(temp_music_dir), "--dest", str(dest)])
        result = runner.invoke(
            main,
            [
                "validate", "FABRICLIVE_72",
                "--dest", str(dest),
                "--source", str(temp_music_dir),
            ],
        )
        assert result.exit_code == 0
        assert "PASSED" in result.output

    def test_validate_fails_on_missing(self, runner, temp_music_dir, tmp_path):
        dest = tmp_path / "playlists"
        runner.invoke(main, ["generate", "--source", str(temp_music_dir), "--dest", str(dest)])
        # Create a fake playlist with nonexistent tracks
        fake_pl = dest / "fake.m3u"
        fake_pl.write_text("#EXTM3U\nnonexistent_file.mp3\n")
        result = runner.invoke(
            main,
            ["validate", "fake", "--dest", str(dest), "--source", str(temp_music_dir)],
        )
        assert result.exit_code != 0
        assert "FAILED" in result.output


class TestDeleteCommand:
    def test_deletes_playlist(self, runner, temp_music_dir, tmp_path):
        dest = tmp_path / "playlists"
        runner.invoke(main, ["generate", "--source", str(temp_music_dir), "--dest", str(dest)])
        assert (dest / "FABRICLIVE_72.m3u").exists()
        result = runner.invoke(main, ["delete", "FABRICLIVE_72", "--dest", str(dest), "--yes"])
        assert result.exit_code == 0
        assert not (dest / "FABRICLIVE_72.m3u").exists()

    def test_delete_missing_playlist(self, runner, tmp_path):
        result = runner.invoke(
            main,
            ["delete", "nonexistent", "--dest", str(tmp_path / "playlists"), "--yes"],
        )
        assert result.exit_code != 0


class TestEndToEnd:
    """Full workflow: generate -> list -> info -> validate -> delete."""

    def test_full_workflow(self, runner, temp_music_dir, tmp_path):
        dest = tmp_path / "playlists"

        # 1. Generate
        result = runner.invoke(main, [
            "generate", "--source", str(temp_music_dir), "--dest", str(dest),
        ])
        assert result.exit_code == 0
        assert (dest / "FABRICLIVE_72.m3u").exists()

        # 2. List
        result = runner.invoke(main, ["list", "--dest", str(dest)])
        assert result.exit_code == 0
        assert "FABRICLIVE_72" in result.output

        # 3. Info
        result = runner.invoke(main, ["info", "FABRICLIVE_72", "--dest", str(dest)])
        assert result.exit_code == 0
        assert "01 - Intro.mp3" in result.output

        # 4. Validate
        result = runner.invoke(
            main,
            ["validate", "FABRICLIVE_72", "--dest", str(dest), "--source", str(temp_music_dir)],
        )
        assert result.exit_code == 0
        assert "PASSED" in result.output

        # 5. Delete
        result = runner.invoke(main, ["delete", "FABRICLIVE_72", "--dest", str(dest), "--yes"])
        assert result.exit_code == 0
        assert not (dest / "FABRICLIVE_72.m3u").exists()

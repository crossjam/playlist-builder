"""Tests for ffmpeg transcoding to .m4a."""

import shutil
import subprocess

import pytest

from playlist_builder.converter import (
    convert_playlist_tracks,
    convert_track,
    is_ffmpeg_available,
)
from playlist_builder.models import Playlist, Track


class TestIsFfmpegAvailable:
    def test_detects_ffmpeg(self):
        if not shutil.which("ffmpeg"):
            pytest.skip("ffmpeg not installed")
        assert is_ffmpeg_available() is True

    def test_returns_false_when_missing(self, monkeypatch):
        def mock_which(cmd):
            return None if cmd == "ffmpeg" else shutil.which(cmd)

        monkeypatch.setattr(shutil, "which", mock_which)
        assert is_ffmpeg_available() is False


class TestConvertTrack:
    def test_convert_mp3_to_m4a(self, tmp_path):
        if not shutil.which("ffmpeg"):
            pytest.skip("ffmpeg not installed")
        src = tmp_path / "test.mp3"
        subprocess.run(
            [
                "ffmpeg", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono",
                "-t", "0.5", "-q:a", "9", str(src),
            ],
            check=True, capture_output=True,
        )
        dest_dir = tmp_path / "converted"
        result = convert_track(Track("test.mp3"), src, dest_dir)
        assert result is not None
        assert result.suffix == ".m4a"

    def test_skips_already_m4a(self, tmp_path):
        result = convert_track(
            Track("already.m4a"), tmp_path / "already.m4a", tmp_path / "converted"
        )
        assert result is None

    def test_skips_if_output_exists(self, tmp_path):
        if not shutil.which("ffmpeg"):
            pytest.skip("ffmpeg not installed")
        src = tmp_path / "src.mp3"
        subprocess.run(
            [
                "ffmpeg", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono",
                "-t", "0.5", "-q:a", "9", str(src),
            ],
            check=True, capture_output=True,
        )
        dest_dir = tmp_path / "converted"
        dest_dir.mkdir()
        existing = dest_dir / "src.m4a"
        existing.touch()
        result = convert_track(Track("src.mp3"), src, dest_dir)
        assert result == existing


class TestConvertPlaylistTracks:
    def test_converts_entire_playlist(self, tmp_path):
        if not shutil.which("ffmpeg"):
            pytest.skip("ffmpeg not installed")
        source_dir = tmp_path / "source"
        album_dir = source_dir / "test"
        album_dir.mkdir(parents=True)
        for name in ["01.mp3", "02.flac", "03.m4a"]:
            subprocess.run(
                [
                    "ffmpeg", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono",
                    "-t", "0.5", str(album_dir / name),
                ],
                check=True, capture_output=True,
            )
        playlist = Playlist(
            name="test",
            tracks=[Track("01.mp3"), Track("02.flac"), Track("03.m4a")],
        )
        dest_dir = tmp_path / "playlists"
        converted = convert_playlist_tracks(playlist, source_dir, dest_dir)
        assert converted.track_count == 3
        for track in converted.tracks:
            assert track.relative_path.endswith(".m4a")
        assert converted.tracks[2].relative_path == "03.m4a"

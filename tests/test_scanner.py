"""Tests for directory scanner."""

from fabric_playlists.scanner import (
    _should_include,
    _should_skip,
    is_audio_file,
    scan_all_directories,
    scan_directory,
)


class TestIsAudioFile:
    def test_mp3_is_audio(self, temp_music_dir):
        assert is_audio_file(temp_music_dir / "FABRICLIVE_72" / "01 - Intro.mp3")

    def test_flac_is_audio(self, temp_music_dir):
        assert is_audio_file(temp_music_dir / "FABRICLIVE_72" / "02 - Mix.flac")

    def test_jpg_is_not_audio(self, temp_music_dir):
        assert not is_audio_file(temp_music_dir / "FABRICLIVE_72" / "cover.jpg")


class TestFilters:
    def test_include_fabriclive(self):
        assert _should_include("FABRICLIVE_72")
        assert _should_include("FABRICLIVE 95 - Test")
        assert _should_include("fabriclive_something")

    def test_include_fabric_presents(self):
        assert _should_include("fabric presents Something")
        assert _should_include("Fabric Presents Vol 2")

    def test_exclude_random_dir(self):
        assert not _should_include("random_mix")
        assert not _should_include("fabric_100")
        assert not _should_include("EmptyAlbum")

    def test_skip_presents_in_name(self):
        assert _should_skip("fabric presents Something")
        assert _should_skip("presents_album")

    def test_skip_archives(self):
        assert _should_skip("wav archives 2019")
        assert _should_skip("Archives Old")


class TestScanDirectory:
    def test_finds_audio_files(self, temp_music_dir):
        tracks = scan_directory(temp_music_dir / "FABRICLIVE_72")
        relative = [t.relative_path for t in tracks]
        assert "01 - Intro.mp3" in relative
        assert "02 - Mix.flac" in relative
        assert len(tracks) == 2

    def test_fabric_presents_has_tracks(self, temp_music_dir):
        """Direct scan of fabric presents dir finds its tracks."""
        tracks = scan_directory(temp_music_dir / "fabric presents Something")
        assert len(tracks) == 2

    def test_handles_nested_dirs(self, temp_music_dir):
        tracks = scan_directory(temp_music_dir / "fabric_100")
        relative = [t.relative_path for t in tracks]
        assert "cd1/01.flac" in relative
        assert "cd2/01.mp3" in relative
        assert len(tracks) == 2

    def test_empty_dir_returns_empty(self, temp_music_dir):
        tracks = scan_directory(temp_music_dir / "EmptyAlbum")
        assert len(tracks) == 0

    def test_continuous_trumps_all(self, temp_music_dir):
        tracks = scan_directory(temp_music_dir / "FABRICLIVE_CONT")
        paths = [t.relative_path for t in tracks]
        assert "continuous.mp3" in paths
        assert "01 - Continuous Mix.flac" in paths
        assert len(paths) == 2
        assert "01 - Intro.flac" not in paths
        assert "03 - Outro.wav" not in paths


class TestScanAllDirectories:
    def test_only_included_dirs_are_scanned(self, temp_music_dir):
        """Only directories matching INCLUDE_PATTERNS appear in results."""
        results = scan_all_directories(temp_music_dir)
        names = [r[0] for r in results]
        assert "FABRICLIVE_72" in names
        assert "FABRICLIVE_CONT" in names
        assert "FABRICLIVE 95 - Test" in names
        assert "fabric presents Something" in names  # include overrides skip
        # Not matching INCLUDE_PATTERNS
        assert "fabric_100" not in names
        assert "EmptyAlbum" not in names
        assert "wav archives 2019" not in names

    def test_returns_empty_for_nonexistent(self, tmp_path):
        results = scan_all_directories(tmp_path / "nonexistent")
        assert results == []


class TestDedupePreferM4a:
    def test_keeps_m4a_over_mp3_same_stem(self, temp_music_dir):
        tracks = scan_directory(temp_music_dir / "FABRICLIVE_99")
        paths = [t.relative_path for t in tracks]
        assert "01 - Intro.m4a" in paths
        assert "01 - Intro.mp3" not in paths

    def test_keeps_both_when_no_m4a_duplicate(self, temp_music_dir):
        tracks = scan_directory(temp_music_dir / "FABRICLIVE_99")
        paths = [t.relative_path for t in tracks]
        assert "02 - Mix.flac" in paths
        assert "02 - Mix.wav" in paths

    def test_dedup_does_not_affect_unique_tracks(self, temp_music_dir):
        tracks = scan_directory(temp_music_dir / "FABRICLIVE_72")
        assert len(tracks) == 2

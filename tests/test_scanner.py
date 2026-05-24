"""Tests for directory scanner."""
from fabric_playlists.scanner import is_audio_file, scan_all_directories, scan_directory


class TestIsAudioFile:
    def test_mp3_is_audio(self, temp_music_dir):
        assert is_audio_file(temp_music_dir / "FABRICLIVE_72" / "01 - Intro.mp3")
    def test_flac_is_audio(self, temp_music_dir):
        assert is_audio_file(temp_music_dir / "FABRICLIVE_72" / "02 - Mix.flac")
    def test_jpg_is_not_audio(self, temp_music_dir):
        assert not is_audio_file(temp_music_dir / "FABRICLIVE_72" / "cover.jpg")

class TestScanDirectory:
    def test_finds_audio_files(self, temp_music_dir):
        tracks = scan_directory(temp_music_dir / "FABRICLIVE_72")
        relative = [t.relative_path for t in tracks]
        assert "01 - Intro.mp3" in relative
        assert "02 - Mix.flac" in relative
        assert len(tracks) == 2
    def test_skips_presents_dir(self, temp_music_dir):
        tracks = scan_directory(temp_music_dir / "fabric presents Something")
        assert len(tracks) == 0
    def test_handles_nested_dirs(self, temp_music_dir):
        tracks = scan_directory(temp_music_dir / "fabric_100")
        relative = [t.relative_path for t in tracks]
        assert "cd1/01.flac" in relative
        assert "cd2/01.mp3" in relative
        assert len(tracks) == 2
    def test_empty_dir_returns_empty(self, temp_music_dir):
        tracks = scan_directory(temp_music_dir / "EmptyAlbum")
        assert len(tracks) == 0

    def test_skips_archives_dir(self, temp_music_dir):
        """Directories with 'archives' in the name should be skipped."""
        tracks = scan_directory(temp_music_dir / "wav archives 2019")
        assert len(tracks) == 0

    def test_continuous_trumps_all(self, temp_music_dir):
        """If a directory has files with 'continuous' in the stem, only those appear."""
        tracks = scan_directory(temp_music_dir / "FABRICLIVE_CONT")
        paths = [t.relative_path for t in tracks]
        assert "continuous.mp3" in paths
        assert "01 - Continuous Mix.flac" in paths
        assert len(paths) == 2
        assert "01 - Intro.flac" not in paths
        assert "03 - Outro.wav" not in paths

class TestScanAllDirectories:
    def test_scans_all_non_presents_dirs(self, temp_music_dir):
        results = scan_all_directories(temp_music_dir)
        names = [r[0] for r in results]
        assert "FABRICLIVE_72" in names
        assert "fabric_100" in names
        assert "FABRICLIVE_CONT" in names
        assert "fabric presents Something" not in names
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

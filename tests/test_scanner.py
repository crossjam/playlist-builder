"""Tests for directory scanner."""
from fabric_playlists.scanner import is_audio_file, scan_directory, scan_all_directories

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

class TestScanAllDirectories:
    def test_scans_all_non_presents_dirs(self, temp_music_dir):
        results = scan_all_directories(temp_music_dir)
        names = [r[0] for r in results]
        assert "FABRICLIVE_72" in names
        assert "fabric_100" in names
        assert "fabric presents Something" not in names
    def test_returns_empty_for_nonexistent(self, tmp_path):
        results = scan_all_directories(tmp_path / "nonexistent")
        assert results == []
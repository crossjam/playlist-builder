"""Tests for playlist I/O operations."""

from playlist_builder.models import Playlist, Track
from playlist_builder.playlist import delete_playlist, list_playlists, read_playlist, write_playlist


class TestWritePlaylist:
    def test_writes_m3u_file(self, tmp_path):
        dest = tmp_path / "playlists"
        p = Playlist(name="test", tracks=[Track("01.flac"), Track("02.mp3")])
        path = write_playlist(p, dest)
        assert path.exists()
        content = path.read_text()
        assert content == "#EXTM3U\n01.flac\n02.mp3\n"

    def test_creates_dest_dir_if_missing(self, tmp_path):
        dest = tmp_path / "nonexistent" / "playlists"
        p = Playlist(name="test", tracks=[Track("song.mp3")])
        path = write_playlist(p, dest)
        assert dest.exists()
        assert path.exists()

    def test_sanitizes_playlist_name(self, tmp_path):
        dest = tmp_path / "playlists"
        p = Playlist(name="bad:name/here?", tracks=[Track("song.mp3")])
        path = write_playlist(p, dest)
        assert ":" not in path.name
        assert "?" not in path.name


class TestReadPlaylist:
    def test_reads_m3u_file(self, tmp_path):
        dest = tmp_path / "playlists"
        playlist_path = dest / "read_test.m3u"
        dest.mkdir(parents=True)
        playlist_path.write_text("#EXTM3U\n01.flac\n02.mp3\n")
        p = read_playlist(playlist_path)
        assert p.name == "read_test"
        assert len(p.tracks) == 2

    def test_returns_none_for_missing_file(self, tmp_path):
        p = read_playlist(tmp_path / "nonexistent.m3u")
        assert p is None


class TestListPlaylists:
    def test_lists_m3u_files(self, tmp_path):
        dest = tmp_path / "playlists"
        dest.mkdir()
        (dest / "a.m3u").touch()
        (dest / "b.m3u").touch()
        (dest / "not_a_playlist.txt").touch()
        playlists = list_playlists(dest)
        names = [p.name for p in playlists]
        assert "a" in names
        assert "b" in names
        assert "not_a_playlist" not in names

    def test_returns_empty_for_missing_dir(self, tmp_path):
        playlists = list_playlists(tmp_path / "nonexistent")
        assert playlists == []


class TestDeletePlaylist:
    def test_deletes_playlist_file(self, tmp_path):
        dest = tmp_path / "playlists"
        dest.mkdir()
        path = dest / "to_delete.m3u"
        path.write_text("#EXTM3U\nsong.mp3\n")
        assert delete_playlist("to_delete", dest) is True
        assert not path.exists()

    def test_returns_false_for_missing(self, tmp_path):
        dest = tmp_path / "playlists"
        dest.mkdir()
        assert delete_playlist("nonexistent", dest) is False

"""Tests for playlist data models."""

from fabric_playlists.models import Playlist, Track, parse_m3u


class TestTrack:
    def test_track_creation(self):
        t = Track(relative_path="01 - Song.flac")
        assert t.relative_path == "01 - Song.flac"
        assert t.extension == ".flac"

    def test_track_sort_order(self):
        tracks = [
            Track("10 - Last.wav"),
            Track("02 - Second.mp3"),
            Track("01 - First.flac"),
        ]
        assert [t.relative_path for t in sorted(tracks)] == [
            "01 - First.flac",
            "02 - Second.mp3",
            "10 - Last.wav",
        ]


class TestPlaylist:
    def test_empty_playlist(self):
        p = Playlist(name="test", tracks=[])
        assert p.name == "test"
        assert len(p.tracks) == 0

    def test_playlist_with_tracks(self):
        p = Playlist(name="my_mix", tracks=[
            Track("01.flac"),
            Track("02.mp3"),
        ])
        assert len(p.tracks) == 2

    def test_m3u_serialization(self):
        p = Playlist(name="test", tracks=[
            Track("01 - First.mp3"),
            Track("02 - Second.wav"),
        ])
        output = p.to_m3u()
        assert output == "#EXTM3U\n01 - First.mp3\n02 - Second.wav\n"

    def test_m3u_parse(self):
        content = "#EXTM3U\n01 - First.mp3\n02 - Second.wav\n"
        p = parse_m3u("test", content)
        assert p.name == "test"
        assert len(p.tracks) == 2
        assert p.tracks[0].relative_path == "01 - First.mp3"

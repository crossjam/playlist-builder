"""Data models for playlists and tracks."""

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Track:
    """A single audio track referenced in a playlist."""
    relative_path: str

    @property
    def extension(self) -> str:
        return Path(self.relative_path).suffix.lower()

    def __lt__(self, other: "Track") -> bool:
        return self.relative_path < other.relative_path


@dataclass
class Playlist:
    """An M3U playlist containing audio tracks."""
    name: str
    tracks: list[Track] = field(default_factory=list)

    @property
    def track_count(self) -> int:
        return len(self.tracks)

    def to_m3u(self) -> str:
        """Serialize playlist to M3U format."""
        lines = ["#EXTM3U"]
        for track in sorted(self.tracks):
            lines.append(track.relative_path)
        return "\n".join(lines) + "\n"

    def __repr__(self) -> str:
        return f"Playlist(name={self.name!r}, tracks={self.track_count})"


def parse_m3u(name: str, content: str) -> Playlist:
    """Parse M3U content string into a Playlist object."""
    tracks = []
    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith("#EXTM3U"):
            continue
        if line.startswith("#"):
            continue
        tracks.append(Track(relative_path=line))
    return Playlist(name=name, tracks=tracks)

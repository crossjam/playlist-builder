"""M3U playlist read/write/validate operations."""

from pathlib import Path

from fabric_playlists.config import _safe_filename
from fabric_playlists.models import Playlist, parse_m3u


def write_playlist(playlist: Playlist, dest_dir: Path) -> Path:
    """Write a Playlist to an .m3u file in dest_dir. Returns the file path."""
    dest_dir.mkdir(parents=True, exist_ok=True)
    safe_name = _safe_filename(playlist.name)
    filepath = dest_dir / f"{safe_name}.m3u"
    filepath.write_text(playlist.to_m3u(), encoding="utf-8")
    return filepath


def read_playlist(filepath: Path) -> Playlist | None:
    """Read an .m3u file and return a Playlist, or None if not found."""
    if not filepath.exists():
        return None
    name = filepath.stem
    content = filepath.read_text(encoding="utf-8")
    return parse_m3u(name, content)


def list_playlists(dest_dir: Path) -> list[Playlist]:
    """List all .m3u playlists in the destination directory."""
    if not dest_dir.is_dir():
        return []
    results = []
    for m3u_file in sorted(dest_dir.glob("*.m3u")):
        name = m3u_file.stem
        content = m3u_file.read_text(encoding="utf-8")
        results.append(parse_m3u(name, content))
    return results


def delete_playlist(name: str, dest_dir: Path) -> bool:
    """Delete a playlist by name. Returns True if deleted, False if not found."""
    safe_name = _safe_filename(name)
    filepath = dest_dir / f"{safe_name}.m3u"
    if filepath.exists():
        filepath.unlink()
        return True
    return False

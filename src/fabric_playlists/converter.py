"""ffmpeg-based audio transcoding to .m4a."""

import shutil
import subprocess
from pathlib import Path

from fabric_playlists.models import Playlist, Track


def is_ffmpeg_available() -> bool:
    """Check if ffmpeg is installed and on PATH."""
    return shutil.which("ffmpeg") is not None


def _detect_aac_encoder() -> str:
    """Return the best available AAC encoder: libfdk_aac or aac."""
    result = subprocess.run(
        ["ffmpeg", "-encoders"], capture_output=True, text=True
    )
    if "libfdk_aac" in result.stdout:
        return "libfdk_aac"
    return "aac"


def convert_track(track: Track, source_file: Path, dest_dir: Path) -> Path | None:
    """Convert a single track to .m4a. Returns output path, or None if already .m4a."""
    if track.extension == ".m4a":
        return None
    output_path = dest_dir / f"{Path(track.relative_path).stem}.m4a"
    if output_path.exists():
        return output_path
    dest_dir.mkdir(parents=True, exist_ok=True)
    encoder = _detect_aac_encoder()
    subprocess.run(
        [
            "ffmpeg", "-i", str(source_file), "-c:a", encoder, "-b:a", "128k",
            "-vn", "-y", str(output_path),
        ],
        check=True, capture_output=True, text=True,
    )
    return output_path


def convert_playlist_tracks(
    playlist: Playlist, source_dir: Path, dest_dir: Path
) -> Playlist:
    """Convert all non-.m4a tracks in a playlist to .m4a.

    Raises RuntimeError if ffmpeg is not installed.
    """
    if not is_ffmpeg_available():
        raise RuntimeError(
            "ffmpeg is not installed or not on PATH. Install ffmpeg to use --convert-to-m4a."
        )
    converted_dir = dest_dir / "converted"
    new_tracks: list[Track] = []
    for track in playlist.tracks:
        source_file = source_dir / playlist.name / track.relative_path
        result = convert_track(track, source_file, converted_dir)
        if result is None:
            new_tracks.append(track)
        else:
            rel = result.relative_to(dest_dir)
            new_tracks.append(Track(relative_path=str(rel)))
    return Playlist(name=playlist.name, tracks=new_tracks)

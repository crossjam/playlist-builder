"""Directory scanner for audio files."""
import os
from collections import defaultdict
from pathlib import Path
from typing import List, Tuple
from fabric_playlists.models import Track

SUPPORTED_EXTENSIONS = {".mp3", ".flac", ".wav", ".m4a", ".ogg"}

def is_audio_file(path: Path) -> bool:
    return path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS

def scan_directory(dir_path: Path) -> List[Track]:
    if not dir_path.is_dir():
        return []
    if "presents" in dir_path.name.lower():
        return []
    tracks = []
    try:
        for root, dirs, files in os.walk(dir_path):
            dirs[:] = [d for d in dirs if "presents" not in d.lower()]
            for filename in files:
                filepath = Path(root) / filename
                if is_audio_file(filepath):
                    rel = filepath.relative_to(dir_path)
                    tracks.append(Track(relative_path=str(rel)))
    except PermissionError:
        pass
    return _dedupe_prefer_m4a(sorted(tracks))


def _dedupe_prefer_m4a(tracks):
    """If multiple tracks share the same stem, keep only .m4a version."""
    by_stem = defaultdict(list)
    for t in tracks:
        stem = Path(t.relative_path).stem
        by_stem[stem].append(t)
    kept = []
    for candidates in by_stem.values():
        m4a = [t for t in candidates if t.extension == ".m4a"]
        kept.extend(m4a if m4a else candidates)
    return sorted(kept)


def scan_all_directories(base_dir: Path) -> List[Tuple[str, List[Track]]]:
    results = []
    if not base_dir.is_dir():
        return results
    for item in sorted(base_dir.iterdir()):
        if not item.is_dir():
            continue
        if "presents" in item.name.lower():
            continue
        tracks = scan_directory(item)
        if tracks:
            results.append((item.name, tracks))
    return results
"""Directory scanner for audio files."""

import os
import re
from collections import defaultdict
from pathlib import Path

from fabric_playlists.models import Track

SUPPORTED_EXTENSIONS = {".mp3", ".flac", ".wav", ".m4a", ".ogg"}


def is_audio_file(path: Path) -> bool:
    return path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS


SKIP_PATTERNS = ["presents", "archives"]
INCLUDE_PATTERNS = ["FABRICLIVE", "fabric presents"]
INCLUDE_REGEX = re.compile(r"fabric\s\d{1,3}", re.IGNORECASE)


def _should_skip(name: str) -> bool:
    """Return True if the directory name should be skipped."""
    lower = name.lower()
    return any(p in lower for p in SKIP_PATTERNS)


def _should_include(name: str) -> bool:
    """Return True if the directory name matches an include pattern."""
    lower = name.lower()
    if any(p.lower() in lower for p in INCLUDE_PATTERNS):
        return True
    return bool(INCLUDE_REGEX.search(name))


def scan_directory(dir_path: Path) -> list[Track]:
    if not dir_path.is_dir():
        return []
    tracks = []
    try:
        for root, dirs, files in os.walk(dir_path):
            dirs[:] = [d for d in dirs if not _should_skip(d)]
            for filename in files:
                filepath = Path(root) / filename
                if is_audio_file(filepath):
                    rel = filepath.relative_to(dir_path)
                    tracks.append(Track(relative_path=str(rel)))
    except PermissionError:
        pass
    tracks = _dedupe_prefer_m4a(sorted(tracks))
    return _filter_continuous(tracks)


def _filter_continuous(tracks: list[Track]) -> list[Track]:
    """If any track's stem contains 'continuous', return only those tracks."""
    continuous = [t for t in tracks if "continuous" in Path(t.relative_path).stem.lower()]
    if continuous:
        return continuous
    return tracks


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


def scan_all_directories(base_dir: Path) -> list[tuple[str, list[Track]]]:
    results = []
    if not base_dir.is_dir():
        return results
    for item in sorted(base_dir.iterdir()):
        if not item.is_dir():
            continue
        if not _should_include(item.name):
            continue
        # No _should_skip here — include overrides skip at the top level
        tracks = scan_directory(item)
        if tracks:
            results.append((item.name, tracks))
    return results

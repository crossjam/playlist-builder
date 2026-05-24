"""Shared test fixtures."""

import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def temp_music_dir():
    """Create a temporary directory structure simulating Fabric folders."""
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        # Normal album dir
        album = base / "FABRICLIVE_72"
        album.mkdir()
        (album / "01 - Intro.mp3").touch()
        (album / "02 - Mix.flac").touch()
        (album / "cover.jpg").touch()
        # Presents dir — should be skipped
        presents = base / "fabric presents Something"
        presents.mkdir()
        (presents / "01 - Track.mp3").touch()
        (presents / "02 - Track.flac").touch()
        # Empty dir
        empty = base / "EmptyAlbum"
        empty.mkdir()
        # Dir with subdirs
        nested = base / "fabric_100"
        nested.mkdir()
        (nested / "cd1" / "01.flac").parent.mkdir(parents=True)
        (nested / "cd1" / "01.flac").touch()
        (nested / "cd2" / "01.mp3").parent.mkdir(parents=True, exist_ok=True)
        (nested / "cd2" / "01.mp3").touch()
        # Dir with duplicate stems (same track, different formats)
        dup = base / "FABRICLIVE_99"
        dup.mkdir()
        (dup / "01 - Intro.mp3").touch()
        (dup / "01 - Intro.m4a").touch()
        (dup / "02 - Mix.flac").touch()
        (dup / "02 - Mix.wav").touch()
        # Archives dir — should be skipped (contains "archives" in name)
        archives = base / "wav archives 2019"
        archives.mkdir()
        (archives / "01 - Old.mp3").touch()
        (archives / "02 - Archive.flac").touch()
        # Dir with a continuous mix file
        continuous = base / "FABRICLIVE_CONT"
        continuous.mkdir()
        (continuous / "01 - Intro.flac").touch()
        (continuous / "continuous.mp3").touch()
        (continuous / "01 - Continuous Mix.flac").touch()
        (continuous / "03 - Outro.wav").touch()
        # Dir with spaces in name
        space_dir = base / "FABRICLIVE 95 - Test"
        space_dir.mkdir()
        (space_dir / "01.flac").touch()
        (space_dir / "02.mp3").touch()
        # Dir matching regex: fabric + space + digit
        fabric72 = base / "fabric 72"
        fabric72.mkdir()
        (fabric72 / "01.flac").touch()
        (fabric72 / "02.wav").touch()
        yield base

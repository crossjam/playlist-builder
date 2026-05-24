# Generate & Manage M3U Playlists for Fabric Directories (v2 — Python Package + Click CLI)

> **For Hermes:** Use subagent-driven-development skill to implement this plan task-by-task.

**Goal:** Build a pip-installable Python package called `fabric-playlists` that provides a `click`-based CLI tool (`fabric-playlists`) for scanning Fabric music directories (excluding "presents") and generating, listing, validating, and deleting `.m3u` playlists.

**Architecture:** Python package with `click` CLI framework. Package structure: `src/fabric_playlists/` with `cli.py` (entry point), `scanner.py` (directory walking + audio discovery + stem-based .m4a deduplication), `playlist.py` (M3U read/write operations), `models.py` (data classes for playlists/tracks), `converter.py` (optional ffmpeg transcoding to .m4a), `config.py` (TOML config via `platformdirs` + env var overrides). Entry point registered via `pyproject.toml`. Dependencies: `click`, `loguru`, `platformdirs`; optional system `ffmpeg`.

**Tech Stack:** Python 3.11+, `click` for CLI, `loguru` for structured logging, `platformdirs` + `tomllib` (stdlib) for TOML configuration, `ty` for type checking, `ruff` for linting, `poethepoet` for task orchestration, `pytest` for testing. Standard library for everything else. Optional: system `ffmpeg` for transcoding.

---

## Package Structure

```
fabric-playlists/
├── pyproject.toml
├── README.md
├── src/
│   └── fabric_playlists/
│       ├── __init__.py
│       ├── cli.py          # Click CLI entry point + commands
│       ├── scanner.py      # Directory walking, audio discovery, m4a dedup
│       ├── playlist.py     # M3U read/write/list/delete
│       ├── models.py       # Dataclasses: Playlist, Track
│       ├── converter.py    # ffmpeg transcoding to .m4a (optional)
│       └── config.py       # TOML config via platformdirs + env overrides
└── tests/
    ├── __init__.py
    ├── test_cli.py
    ├── test_scanner.py
    ├── test_playlist.py
    ├── test_converter.py
    ├── test_config.py
    └── conftest.py         # Fixtures: temp dirs with fake audio files
```

## CLI Commands

```
fabric-playlists [--verbose] [--config PATH] COMMAND ...
fabric-playlists generate [--convert-to-m4a]  Scan Fabric dirs and create playlists
fabric-playlists list                          List all generated playlists
fabric-playlists validate NAME                 Check that playlist entries point to real files
fabric-playlists info NAME                     Show details about a specific playlist
fabric-playlists delete NAME                   Remove a playlist file
fabric-playlists init                           Bootstrap config dir + default config.toml
fabric-playlists version                       Show the installed version
```

## Configuration

Defaults (source / destination) configurable via:
1. CLI flags: `--source`, `--dest` on every command
2. Environment variables: `FABRIC_SOURCE`, `FABRIC_DEST`, `FABRIC_LOG_LEVEL`
3. TOML config file: `~/.config/fabric-playlists/config.toml` (platform-specific via `platformdirs`; bootstrap with `fabric-playlists init`)

---

### Task 1: Scaffold package structure and pyproject.toml

**Objective:** Create the directory layout, pyproject.toml with Click dependency, and a stub CLI entry point that runs.

**Files:**
- Create: `fabric-playlists/pyproject.toml`
- Create: `fabric-playlists/src/fabric_playlists/__init__.py`
- Create: `fabric-playlists/src/fabric_playlists/cli.py`
- Create: `fabric-playlists/src/fabric_playlists/models.py`
- Create: `fabric-playlists/src/fabric_playlists/scanner.py`
- Create: `fabric-playlists/src/fabric_playlists/converter.py`
- Create: `fabric-playlists/src/fabric_playlists/config.py`
- Create: `fabric-playlists/src/fabric_playlists/playlist.py`
- Create: `fabric-playlists/tests/__init__.py`
- Create: `fabric-playlists/tests/conftest.py`
- Create: `fabric-playlists/tests/test_converter.py`

**Step 1: Write pyproject.toml**

```toml
[build-system]
requires = ["setuptools>=68.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "fabric-playlists"
version = "0.1.0"
description = "CLI tool to generate and manage M3U playlists for Fabric music directories"
requires-python = ">=3.11"
dependencies = [
    "click>=8.1",
    "loguru>=0.7",
    "platformdirs>=4.0",
]

[project.optional-dependencies]
dev = [
    "poethepoet>=0.26",
    "ruff>=0.4",
    "ty>=0.5",
    "pytest>=8.0",
]

[project.scripts]
fabric-playlists = "fabric_playlists.cli:main"

[tool.setuptools.package-dir]
"" = "src"

[tool.setuptools.packages.find]
where = ["src"]

[tool.poe.tasks]
lint = "ruff check src/ tests/"
lint-fix = "ruff check --fix src/ tests/"
typecheck = "ty src/"
test = "pytest tests/ -v"
qa = [
    { cmd = "ruff check src/ tests/" },
    { cmd = "ty src/" },
    { cmd = "pytest tests/ -v" },
]

[tool.ruff]
target-version = "py311"
line-length = 100
select = ["E", "F", "I", "N", "W", "UP", "B", "SIM", "C4"]
ignore = []

[tool.ruff.lint.isort]
known-first-party = ["fabric_playlists"]

[tool.ty]
python-version = "3.11"
strict = true
```

**Step 2: Write stub cli.py**

```python
"""CLI entry point for fabric-playlists."""

import click

@click.group()
def main():
    """Manage M3U playlists for Fabric music directories."""
    pass


@main.command()
def generate():
    """Scan Fabric directories and generate M3U playlists."""
    click.echo("Not implemented yet.")


@main.command()
def list():
    """List all generated playlists."""
    click.echo("Not implemented yet.")


if __name__ == "__main__":
    main()
```

**Step 3: Write empty stub files**

- `__init__.py`: `"""fabric-playlists — manage M3U playlists for Fabric music directories."""`
- `models.py`: `"""Data models for playlists and tracks."""`
- `scanner.py`: `"""Directory scanner for audio files."""`
- `converter.py`: `"""ffmpeg-based audio transcoding to .m4a."""`
- `config.py`: `"""TOML configuration via platformdirs + env var overrides."""`
- `playlist.py`: `"""M3U playlist operations."""`
- `tests/__init__.py`: empty
- `tests/conftest.py`: `"""Shared test fixtures."""`
- `tests/test_config.py`: `"""Tests for configuration module."""`

**Step 4: Run tests**

```bash
cd fabric-playlists
pip install -e ".[dev]"
```
Expected: package installs, no errors.

**Step 5: Verify CLI works**

```bash
fabric-playlists --help
```
Expected: shows command group with `generate` and `list` subcommands.

**Step 6: Commit**

```bash
git add fabric-playlists/
git commit -m "feat: scaffold fabric-playlists package with Click CLI stubs"
```

---

### Task 2: Define data models (Playlist, Track)

**Objective:** Create dataclasses to represent playlists and tracks, with M3U parsing/serialization.

**Files:**
- Modify: `fabric-playlists/src/fabric_playlists/models.py`
- Create: `fabric-playlists/tests/test_models.py`

**Step 1: Write failing test**

```python
"""Tests for playlist data models."""

from fabric_playlists.models import Track, Playlist, parse_m3u


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
```

**Step 2: Run test to verify failure**

```bash
cd fabric-playlists && python -m pytest tests/test_models.py -v
```
Expected: FAIL — ImportError (module not written yet).

**Step 3: Write minimal implementation**

```python
"""Data models for playlists and tracks."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import List


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
    tracks: List[Track] = field(default_factory=list)

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
```

**Step 4: Run test to verify pass**

```bash
cd fabric-playlists && python -m pytest tests/test_models.py -v
```
Expected: PASS (6 tests).

**Step 5: Commit**

```bash
git add fabric-playlists/src/fabric_playlists/models.py fabric-playlists/tests/test_models.py
git commit -m "feat: add Playlist and Track dataclasses with M3U serialization"
```

---

### Task 2b: Configuration and logging — TOML + platformdirs + loguru

**Objective:** Create a `config.py` module that loads settings from a TOML file stored in the platform-appropriate config directory (via `platformdirs`), merges environment variable overrides, and set up `loguru` for structured logging throughout the CLI. The `--verbose`/`-v` flag and `--config` flag are added as global Click options.

**Files:**
- Create: `fabric-playlists/src/fabric_playlists/config.py`
- Create: `fabric-playlists/tests/test_config.py`

**Design decisions:**

| Decision | Choice | Rationale |
|---|---|---|
| Config location | `platformdirs.user_config_dir("fabric-playlists")` | OS-correct: `~/.config/fabric-playlists/` on Linux, `~/Library/Application Support/` on macOS, `%APPDATA%` on Windows |
| Config format | TOML (`tomllib` in stdlib, 3.11+) | Readable, no extra dep, matches `pyproject.toml` |
| Precedence | TOML file → env vars → CLI flags → defaults | Standard layering: CLI trumps env trumps file trumps code |
| Logging | `loguru` (remove default handler, add stderr handler) | Clean structured output; `--verbose` maps to DEBUG |
| Missing config | Silent fallback to hardcoded defaults | Don't fail if no config file exists |
| `--init-config` | `fabric-playlists init` subcommand | Bootstraps a default config file for the user |

**Step 1: Write failing test**

```python
"""Tests for configuration module."""

import os
import tomllib
from pathlib import Path

import pytest
from fabric_playlists.config import (
    AppConfig,
    get_config_dir,
    get_config_path,
    load_config,
    init_config,
)


class TestConfigPaths:
    def test_get_config_dir_returns_platformdirs_path(self):
        path = get_config_dir()
        assert "fabric-playlists" in str(path)

    def test_get_config_path_returns_toml_file(self):
        path = get_config_path()
        assert path.name == "config.toml"


class TestAppConfig:
    def test_default_values(self):
        cfg = AppConfig()
        assert cfg.source == "/mnt/synologynas/Raw Music/Fabric"
        assert cfg.dest == "/mnt/synologynas/Raw Music/playlists"
        assert cfg.log_level == "INFO"

    def test_from_toml_parses_valid_file(self, tmp_path):
        toml_path = tmp_path / "config.toml"
        toml_path.write_text("""
source = "/custom/source"
dest = "/custom/dest"
log_level = "DEBUG"
""")
        cfg = AppConfig.from_toml(toml_path)
        assert cfg.source == "/custom/source"
        assert cfg.dest == "/custom/dest"
        assert cfg.log_level == "DEBUG"

    def test_from_toml_missing_file_returns_defaults(self, tmp_path):
        cfg = AppConfig.from_toml(tmp_path / "nonexistent.toml")
        assert cfg.source == "/mnt/synologynas/Raw Music/Fabric"

    def test_from_toml_partial_file_fills_defaults(self, tmp_path):
        toml_path = tmp_path / "partial.toml"
        toml_path.write_text('source = "/only/source"\n')
        cfg = AppConfig.from_toml(toml_path)
        assert cfg.source == "/only/source"
        assert cfg.dest == "/mnt/synologynas/Raw Music/playlists"  # default

    def test_with_env_overrides_applies_env_vars(self, monkeypatch, tmp_path):
        monkeypatch.setenv("FABRIC_SOURCE", "/env/source")
        monkeypatch.setenv("FABRIC_LOG_LEVEL", "DEBUG")
        cfg = AppConfig()
        cfg = cfg.with_env_overrides()
        assert cfg.source == "/env/source"
        assert cfg.log_level == "DEBUG"

    def test_env_overrides_dont_affect_unset_fields(self, monkeypatch):
        monkeypatch.setenv("FABRIC_SOURCE", "/env/source")
        cfg = AppConfig()
        cfg = cfg.with_env_overrides()
        assert cfg.dest == "/mnt/synologynas/Raw Music/playlists"  # unchanged


class TestLoadConfig:
    def test_load_config_merges_toml_and_env(self, monkeypatch, tmp_path):
        toml_path = tmp_path / "config.toml"
        toml_path.write_text('source = "/file/source"\ndest = "/file/dest"\n')
        monkeypatch.setenv("FABRIC_SOURCE", "/env/source")

        cfg = load_config(toml_path)
        assert cfg.source == "/env/source"  # env wins
        assert cfg.dest == "/file/dest"     # file fallback


class TestInitConfig:
    def test_creates_config_file_if_missing(self, tmp_path):
        target = tmp_path / "config.toml"
        cfg = init_config(target)
        assert target.exists()
        content = target.read_text()
        assert "source" in content
        assert "log_level" in content

    def test_does_not_overwrite_existing(self, tmp_path):
        target = tmp_path / "config.toml"
        target.write_text('source = "/custom"\n')
        cfg = init_config(target)
        assert cfg.source == "/custom"


def test_safe_filename_helper():
    from fabric_playlists.config import _safe_filename
    assert _safe_filename("bad:name?") == "bad_name_"
    assert _safe_filename("  spaces  ") == "spaces"
    assert _safe_filename("") == "unnamed"
```

**Step 2: Run test to verify failure**

```bash
cd fabric-playlists && python -m pytest tests/test_config.py -v
```
Expected: FAIL — ImportError (config.py not written).

**Step 3: Write minimal implementation**

```python
"""TOML configuration via platformdirs + env var overrides."""

import os
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import platformdirs

APP_NAME = "fabric-playlists"


def get_config_dir() -> Path:
    """Platform-appropriate config directory (no roaming, no author)."""
    return Path(platformdirs.user_config_dir(APP_NAME, roaming=False))


def get_config_path() -> Path:
    """Full path to config.toml."""
    return get_config_dir() / "config.toml"


UNSAFE_CHARS = str.maketrans({
    ":": "_", "/": "_", "\\": "_", "?": "_",
    "*": "_", '"': "_", "<": "_", ">": "_", "|": "_",
})


def _safe_filename(name: str) -> str:
    """Convert a name to a safe filename."""
    name = name.translate(UNSAFE_CHARS).strip(" .")
    return name or "unnamed"


@dataclass
class AppConfig:
    """Application configuration with TOML + env var support.

    Precedence: CLI flags > env vars > TOML file > defaults.
    """
    source: str = "/mnt/synologynas/Raw Music/Fabric"
    dest: str = "/mnt/synologynas/Raw Music/playlists"
    log_level: str = "INFO"

    @classmethod
    def from_toml(cls, path: Optional[Path] = None) -> "AppConfig":
        """Load config from TOML file, falling back to defaults if missing."""
        path = path or get_config_path()
        if not path.exists():
            return cls()

        with open(path, "rb") as f:
            data = tomllib.load(f)

        return cls(
            source=data.get("source", cls.source),
            dest=data.get("dest", cls.dest),
            log_level=data.get("log_level", cls.log_level),
        )

    def with_env_overrides(self) -> "AppConfig":
        """Apply environment variable overrides (FABRIC_SOURCE, etc.)."""
        return AppConfig(
            source=os.environ.get("FABRIC_SOURCE", self.source),
            dest=os.environ.get("FABRIC_DEST", self.dest),
            log_level=os.environ.get("FABRIC_LOG_LEVEL", self.log_level),
        )


def load_config(config_path: Optional[Path] = None) -> AppConfig:
    """Load and merge configuration: TOML file → env vars."""
    return AppConfig.from_toml(config_path).with_env_overrides()


def init_config(config_path: Optional[Path] = None):
    """Create a default config file if one doesn't exist. Returns loaded config."""
    config_dir = get_config_dir()
    config_dir.mkdir(parents=True, exist_ok=True)
    target = config_path or get_config_path()
    if not target.exists():
        default = """\
# fabric-playlists configuration
# Environment variables (FABRIC_SOURCE, FABRIC_DEST, FABRIC_LOG_LEVEL)
# override these values.

source = "/mnt/synologynas/Raw Music/Fabric"
dest = "/mnt/synologynas/Raw Music/playlists"
log_level = "INFO"
"""
        target.write_text(default)
    return load_config(target)
```

**Step 4: Run test to verify pass**

```bash
cd fabric-playlists && python -m pytest tests/test_config.py -v
```
Expected: PASS (10 tests).

**Step 5: Commit**

```bash
git add fabric-playlists/src/fabric_playlists/config.py fabric-playlists/tests/test_config.py
git commit -m "feat: add TOML config via platformdirs + env var overrides"
```

---

### Task 3: Build directory scanner

**Objective:** Implement scanner that walks a directory tree, finds audio files, and skips "presents" subdirectories.

**Files:**
- Modify: `fabric-playlists/src/fabric_playlists/scanner.py`
- Create: `fabric-playlists/tests/test_scanner.py`
- Modify: `fabric-playlists/tests/conftest.py` (add fixture for temp music dir)

**Step 1: Add test fixture to conftest.py**

```python
"""Shared test fixtures."""

import os
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
        (album / "cover.jpg").touch()  # Non-audio, should be ignored

        # Presents dir — should be skipped entirely
        presents = base / "fabric presents Something"
        presents.mkdir()
        (presents / "01 - Track.mp3").touch()
        (presents / "02 - Track.flac").touch()

        # Empty dir — should produce no playlist
        empty = base / "EmptyAlbum"
        empty.mkdir()

        # Dir with subdirs
        nested = base / "fabric_100"
        nested.mkdir()
        (nested / "cd1" / "01.flac").parent.mkdir(parents=True)
        (nested / "cd1" / "01.flac").touch()
        (nested / "cd2" / "01.mp3").parent.mkdir(parents=True, exist_ok=True)
        (nested / "cd2" / "01.mp3").touch()

        yield base
```

**Step 2: Write failing test**

```python
"""Tests for directory scanner."""

from pathlib import Path

from fabric_playlists.scanner import (
    SUPPORTED_EXTENSIONS,
    is_audio_file,
    scan_directory,
    scan_all_directories,
)


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
        assert len(tracks) == 2  # cover.jpg skipped

    def test_skips_presents_dir(self, temp_music_dir):
        tracks = scan_directory(temp_music_dir / "fabric presents Something")
        assert len(tracks) == 0  # Entire dir skipped

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
```

**Step 3: Run test to verify failure**

```bash
cd fabric-playlists && python -m pytest tests/test_scanner.py -v
```
Expected: FAIL — ImportError.

**Step 4: Write minimal implementation**

```python
"""Directory scanner for audio files."""

import os
from pathlib import Path
from typing import List, Tuple

from fabric_playlists.models import Track

SUPPORTED_EXTENSIONS = {".mp3", ".flac", ".wav", ".m4a", ".ogg"}


def is_audio_file(path: Path) -> bool:
    """Check if a file has a supported audio extension."""
    return path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS


def scan_directory(dir_path: Path) -> List[Track]:
    """Walk a directory recursively, collecting audio files.
    
    Skips any subdirectory whose name contains 'presents' (case-insensitive).
    """
    if not dir_path.is_dir():
        return []
    if "presents" in dir_path.name.lower():
        return []

    tracks = []
    for root, dirs, files in os.walk(dir_path):
        # Filter out presents subdirectories in-place
        dirs[:] = [d for d in dirs if "presents" not in d.lower()]
        for filename in files:
            filepath = Path(root) / filename
            if is_audio_file(filepath):
                rel = filepath.relative_to(dir_path)
                tracks.append(Track(relative_path=str(rel)))

    return sorted(tracks)


def scan_all_directories(
    base_dir: Path,
) -> List[Tuple[str, List[Track]]]:
    """Scan all subdirectories of base_dir, returning (name, tracks) tuples.
    
    Directories whose name contains 'presents' (case-insensitive) are skipped.
    """
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
```

**Step 5: Run test to verify pass**

```bash
cd fabric-playlists && python -m pytest tests/test_scanner.py -v
```
Expected: PASS (8 tests).

**Step 6: Commit**

```bash
git add fabric-playlists/src/fabric_playlists/scanner.py fabric-playlists/tests/test_scanner.py fabric-playlists/tests/conftest.py
git commit -m "feat: add directory scanner with presents-skip logic"
```

---

### Task 3b: Add stem-based deduplication, preferring .m4a

**Objective:** When a directory has multiple audio files with the same stem (e.g., `01 - Track.flac` and `01 - Track.m4a`), keep only the `.m4a` version and drop the duplicates. This runs as a post-processing step inside `scan_directory()`.

**Files:**
- Modify: `fabric-playlists/src/fabric_playlists/scanner.py`
- Modify: `fabric-playlists/tests/test_scanner.py` (add dedup tests)
- Modify: `fabric-playlists/tests/conftest.py` (add fixture dir with duplicates)

**Step 1: Add test fixture in conftest.py**

```python
    # Dir with duplicate stems (same track, different formats)
    dup = base / "FABRICLIVE_99"
    dup.mkdir()
    (dup / "01 - Intro.mp3").touch()
    (dup / "01 - Intro.m4a").touch()    # same stem, m4a wins
    (dup / "02 - Mix.flac").touch()
    (dup / "02 - Mix.wav").touch()      # same stem, no m4a → keep both? no, keep .wav (prioritize any)

    yield base
```

Note: place this BEFORE the `yield base` line. The dedup should prefer .m4a over everything; when no .m4a exists among duplicates, keep all.

**Step 2: Write failing test**

Add to `test_scanner.py`:

```python
class TestDedupePreferM4a:
    def test_keeps_m4a_over_mp3_same_stem(self, temp_music_dir):
        """When same stem exists as .mp3 and .m4a, keep only .m4a."""
        tracks = scan_directory(temp_music_dir / "FABRICLIVE_99")
        paths = [t.relative_path for t in tracks]
        assert "01 - Intro.m4a" in paths
        assert "01 - Intro.mp3" not in paths

    def test_keeps_both_when_no_m4a_duplicate(self, temp_music_dir):
        """When .flac and .wav share a stem but no .m4a, keep both."""
        tracks = scan_directory(temp_music_dir / "FABRICLIVE_99")
        paths = [t.relative_path for t in tracks]
        # Both kept since neither is .m4a
        assert "02 - Mix.flac" in paths
        assert "02 - Mix.wav" in paths

    def test_dedup_does_not_affect_unique_tracks(self, temp_music_dir):
        """Unique tracks should pass through unchanged."""
        tracks = scan_directory(temp_music_dir / "FABRICLIVE_72")
        assert len(tracks) == 2  # No changes since stems are unique
```

**Step 3: Run test to verify failure**

```bash
cd fabric-playlists && python -m pytest tests/test_scanner.py::TestDedupePreferM4a -v
```
Expected: FAIL — `01 - Intro.mp3` still appears, or test errors due to missing fixture.

**Step 4: Write minimal implementation**

Add to `scanner.py`, call at the end of `scan_directory()`:

```python
def _dedupe_prefer_m4a(tracks: List[Track]) -> List[Track]:
    """If multiple tracks share the same stem, keep only .m4a version.
    
    When no .m4a exists among the duplicates, all versions are kept.
    """
    from collections import defaultdict

    by_stem: dict[str, list[Track]] = defaultdict(list)
    for t in tracks:
        stem = Path(t.relative_path).stem
        by_stem[stem].append(t)

    kept = []
    for stem, candidates in by_stem.items():
        m4a = [t for t in candidates if t.extension == ".m4a"]
        if m4a:
            kept.extend(m4a)
        else:
            kept.extend(candidates)

    return sorted(kept)
```

Update `scan_directory()` to call it:

```python
def scan_directory(dir_path: Path) -> List[Track]:
    # ... existing walk and collection code ...
    
    return _dedupe_prefer_m4a(sorted(tracks))  # was: return sorted(tracks)
```

**Step 5: Run test to verify pass**

```bash
cd fabric-playlists && python -m pytest tests/test_scanner.py -v
```
Expected: PASS (all scanner tests, including 3 new dedup tests = 11 total).

**Step 6: Commit**

```bash
git add fabric-playlists/src/fabric_playlists/scanner.py fabric-playlists/tests/test_scanner.py fabric-playlists/tests/conftest.py
git commit -m "feat: add stem-based deduplication preferring .m4a"
```

---

### Task 4: Implement M3U playlist read/write operations

**Objective:** Add functions to write playlist files, read them back, list them, and delete them from the destination directory.

**Files:**
- Modify: `fabric-playlists/src/fabric_playlists/playlist.py`
- Create: `fabric-playlists/tests/test_playlist.py` (test file — note: separate from test_models.py)

**Step 1: Write failing test**

```python
"""Tests for playlist I/O operations."""

from pathlib import Path

import pytest

from fabric_playlists.models import Playlist, Track
from fabric_playlists.playlist import (
    write_playlist,
    read_playlist,
    list_playlists,
    delete_playlist,
)


class TestWritePlaylist:
    def test_writes_m3u_file(self, tmp_path):
        dest = tmp_path / "playlists"
        p = Playlist(name="test", tracks=[
            Track("01.flac"),
            Track("02.mp3"),
        ])
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
        # Name with special chars should be sanitized
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
```

**Step 2: Run test to verify failure**

```bash
cd fabric-playlists && python -m pytest tests/test_playlist.py -v
```
Expected: FAIL — ImportError.

**Step 3: Write minimal implementation**

```python
"""M3U playlist read/write/validate operations."""

from pathlib import Path
from typing import List, Optional

from fabric_playlists.models import Playlist, parse_m3u


UNSAFE_CHARS = str.maketrans({":": "_", "/": "_", "\\": "_", "?": "_",
                                "*": "_", '"': "_", "<": "_", ">": "_", "|": "_"})


def _safe_filename(name: str) -> str:
    """Convert a name to a safe filename."""
    name = name.translate(UNSAFE_CHARS).strip(" .")
    return name or "unnamed"


def write_playlist(playlist: Playlist, dest_dir: Path) -> Path:
    """Write a Playlist to an .m3u file in dest_dir. Returns the file path."""
    dest_dir.mkdir(parents=True, exist_ok=True)
    safe_name = _safe_filename(playlist.name)
    filepath = dest_dir / f"{safe_name}.m3u"
    filepath.write_text(playlist.to_m3u(), encoding="utf-8")
    return filepath


def read_playlist(filepath: Path) -> Optional[Playlist]:
    """Read an .m3u file and return a Playlist, or None if not found."""
    if not filepath.exists():
        return None
    name = filepath.stem
    content = filepath.read_text(encoding="utf-8")
    return parse_m3u(name, content)


def list_playlists(dest_dir: Path) -> List[Playlist]:
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
```

**Step 4: Run test to verify pass**

```bash
cd fabric-playlists && python -m pytest tests/test_playlist.py -v
```
Expected: PASS (9 tests).

**Step 5: Commit**

```bash
git add fabric-playlists/src/fabric_playlists/playlist.py fabric-playlists/tests/test_playlist.py
git commit -m "feat: add playlist I/O — write, read, list, delete"
```

---

### Task 4b: Add ffmpeg transcoding to .m4a

**Objective:** When `--convert-to-m4a` is passed to `generate`, transcode non-.m4a tracks to .m4a and update the playlist to reference the converted files. Requires `ffmpeg` on the system PATH.

**Files:**
- Create: `fabric-playlists/src/fabric_playlists/converter.py`
- Create: `fabric-playlists/tests/test_converter.py`

**Design decisions:**

| Decision | Choice | Rationale |
|---|---|---|
| Output location | `{dest_dir}/converted/{track_relative_path_stem}.m4a` | Keeps originals untouched; flat converted dir |
| ffmpeg flags | `-c:a libfdk_aac` (fallback `aac`), `-b:a 128k`, `-vn` | FDK AAC at 128k; built-in AAC at 128k if FDK unavailable; strip non-audio streams |
| Skip existing? | Yes — skip if output already exists | Avoids redundant re-encodes |
| Missing ffmpeg? | Raise `RuntimeError` with clear message | Don't silently skip — user asked for conversion |
| Track path update | `Track(relative_path=str(converted_output.relative_to(dest_dir)))` | Playlist references converted files portably |

**Step 1: Write failing test**

```python
"""Tests for ffmpeg transcoding to .m4a."""

import shutil
from pathlib import Path

import pytest

from fabric_playlists.converter import (
    is_ffmpeg_available,
    convert_track,
    convert_playlist_tracks,
)
from fabric_playlists.models import Track, Playlist


class TestIsFfmpegAvailable:
    def test_detects_ffmpeg(self):
        """If ffmpeg is installed, this passes. If not, skip."""
        if not shutil.which("ffmpeg"):
            pytest.skip("ffmpeg not installed")
        assert is_ffmpeg_available() is True

    def test_returns_false_when_missing(self, monkeypatch):
        """Simulate ffmpeg not on PATH."""
        def mock_which(cmd):
            if cmd == "ffmpeg":
                return None
            return shutil.which(cmd)
        monkeypatch.setattr(shutil, "which", mock_which)
        assert is_ffmpeg_available() is False


class TestConvertTrack:
    def test_convert_mp3_to_m4a(self, tmp_path):
        if not shutil.which("ffmpeg"):
            pytest.skip("ffmpeg not installed")
        # Create a tiny valid MP3 using ffmpeg itself
        src = tmp_path / "test.mp3"
        # Generate 1 second of silence as MP3
        import subprocess
        subprocess.run([
            "ffmpeg", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono",
            "-t", "0.5", "-q:a", "9", str(src),
        ], check=True, capture_output=True)

        dest_dir = tmp_path / "converted"
        result = convert_track(Track("test.mp3"), src, dest_dir)
        assert result.suffix == ".m4a"
        assert dest_dir.exists()

    def test_skips_already_m4a(self, tmp_path):
        """m4a tracks should be returned as-is, no conversion."""
        result = convert_track(
            Track("already.m4a"),
            tmp_path / "already.m4a",
            tmp_path / "converted",
        )
        assert result is None  # None means "already .m4a, no conversion needed"

    def test_skips_if_output_exists(self, tmp_path):
        if not shutil.which("ffmpeg"):
            pytest.skip("ffmpeg not installed")
        import subprocess

        src = tmp_path / "src.mp3"
        subprocess.run([
            "ffmpeg", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono",
            "-t", "0.5", "-q:a", "9", str(src),
        ], check=True, capture_output=True)

        dest_dir = tmp_path / "converted"
        dest_dir.mkdir()
        existing = dest_dir / "src.m4a"
        existing.touch()

        result = convert_track(Track("src.mp3"), src, dest_dir)
        assert result == existing  # Returns existing path directly


class TestConvertPlaylistTracks:
    def test_converts_entire_playlist(self, tmp_path):
        if not shutil.which("ffmpeg"):
            pytest.skip("ffmpeg not installed")
        import subprocess

        source_dir = tmp_path / "source"
        source_dir.mkdir()
        for name in ["01.mp3", "02.flac", "03.m4a"]:
            subprocess.run([
                "ffmpeg", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono",
                "-t", "0.5", str(source_dir / name),
            ], check=True, capture_output=True)

        playlist = Playlist(name="test", tracks=[
            Track("01.mp3"),
            Track("02.flac"),
            Track("03.m4a"),
        ])
        dest_dir = tmp_path / "playlists"
        converted = convert_playlist_tracks(playlist, source_dir, dest_dir)

        assert converted.track_count == 3
        for track in converted.tracks:
            assert track.relative_path.endswith(".m4a")
        # m4a track path should be unchanged
        assert converted.tracks[2].relative_path == "03.m4a"
```

**Step 2: Run test to verify failure**

```bash
cd fabric-playlists && python -m pytest tests/test_converter.py -v
```
Expected: FAIL — ImportError (converter.py not written).

**Step 3: Write minimal implementation**

```python
"""ffmpeg-based audio transcoding to .m4a."""

import shutil
import subprocess
from pathlib import Path
from typing import Optional

from fabric_playlists.models import Track, Playlist


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


def convert_track(
    track: Track,
    source_file: Path,
    dest_dir: Path,
) -> Optional[Path]:
    """Convert a single track to .m4a using ffmpeg.

    Args:
        track: The track to convert.
        source_file: Full path to the source audio file.
        dest_dir: Directory to write the converted .m4a file.

    Returns:
        Path to the converted .m4a file, or None if the track is already .m4a
        (no conversion needed — caller should use original path).
    """
    if track.extension == ".m4a":
        return None  # Already .m4a, no conversion needed

    output_path = dest_dir / f"{Path(track.relative_path).stem}.m4a"

    if output_path.exists():
        return output_path  # Already converted

    dest_dir.mkdir(parents=True, exist_ok=True)
    encoder = _detect_aac_encoder()

    subprocess.run(
        [
            "ffmpeg",
            "-i", str(source_file),
            "-c:a", encoder,
            "-b:a", "128k",
            "-vn",              # strip non-audio streams
            "-y",               # overwrite (shouldn't happen due to check above)
            str(output_path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    return output_path


def convert_playlist_tracks(
    playlist: Playlist,
    source_dir: Path,
    dest_dir: Path,
) -> Playlist:
    """Convert all non-.m4a tracks in a playlist to .m4a.

    Args:
        playlist: Playlist whose tracks should be converted.
        source_dir: Base directory where source audio files live.
        dest_dir: Directory to write converted .m4a files (a 'converted/'
                  subdirectory will be created inside it).

    Returns:
        New Playlist with updated track paths pointing to .m4a files.

    Raises:
        RuntimeError: If ffmpeg is not available.
    """
    if not is_ffmpeg_available():
        raise RuntimeError(
            "ffmpeg is not installed or not on PATH. "
            "Install ffmpeg to use --convert-to-m4a."
        )

    converted_dir = dest_dir / "converted"
    new_tracks = []

    for track in playlist.tracks:
        source_file = source_dir / playlist.name / track.relative_path
        result = convert_track(track, source_file, converted_dir)

        if result is None:
            # Already .m4a — keep original relative path
            new_tracks.append(track)
        else:
            # Converted — reference relative to dest_dir for portability
            rel = result.relative_to(dest_dir)
            new_tracks.append(Track(relative_path=str(rel)))

    return Playlist(name=playlist.name, tracks=new_tracks)
```

**Step 4: Run test to verify pass**

```bash
cd fabric-playlists && python -m pytest tests/test_converter.py -v
```
Expected: PASS (5 tests, ffmpeg-dependent ones skipped if not installed).

**Step 5: Commit**

```bash
git add fabric-playlists/src/fabric_playlists/converter.py fabric-playlists/tests/test_converter.py
git commit -m "feat: add ffmpeg-based .m4a transcoding with converter module"
```

---

### Task 5: Implement `generate` CLI command with --convert-to-m4a

**Objective:** Wire the scanner + playlist writer + optional transcoding into the `generate` Click command with `--source`, `--dest`, and `--convert-to-m4a` options and env var fallback.

**Files:**
- Modify: `fabric-playlists/src/fabric_playlists/cli.py`
- Create: `fabric-playlists/tests/test_cli.py` (tests for generate command)

**Step 1: Write failing test**

```python
"""Tests for CLI commands."""

from pathlib import Path

from click.testing import CliRunner
from fabric_playlists.cli import main


@pytest.fixture
def runner():
    return CliRunner()


class TestGenerateCommand:
    def test_generate_creates_playlists(self, runner, temp_music_dir, tmp_path):
        dest = tmp_path / "playlists"
        result = runner.invoke(main, [
            "generate",
            "--source", str(temp_music_dir),
            "--dest", str(dest),
        ])
        assert result.exit_code == 0
        # Should create playlists for non-presents dirs with audio
        assert (dest / "FABRICLIVE_72.m3u").exists()
        assert (dest / "fabric_100.m3u").exists()
        # Should not create for presents
        assert not (dest / "fabric presents Something.m3u").exists()
        # Should not create for empty dir
        assert not (dest / "EmptyAlbum.m3u").exists()

    def test_generate_shows_count(self, runner, temp_music_dir, tmp_path):
        dest = tmp_path / "playlists"
        result = runner.invoke(main, [
            "generate",
            "--source", str(temp_music_dir),
            "--dest", str(dest),
        ])
        assert result.exit_code == 0
        assert "FABRICLIVE_72" in result.output
        assert "2 tracks" in result.output or "track" in result.output.lower()

    def test_generate_source_not_found(self, runner, tmp_path):
        result = runner.invoke(main, [
            "generate",
            "--source", "/nonexistent/path",
            "--dest", str(tmp_path),
        ])
        assert result.exit_code != 0


class TestVersionCommand:
    def test_version_output(self, runner):
        result = runner.invoke(main, ["version"])
        assert result.exit_code == 0
        assert "0.1.0" in result.output
```

**Step 2: Run test to verify failure**

```bash
cd fabric-playlists && python -m pytest tests/test_cli.py -v
```
Expected: FAIL — directory not found error, or missing fixture (need to import pytest).

**Step 3: Write minimal implementation in cli.py**

```python
"""CLI entry point for fabric-playlists."""

import sys
from importlib.metadata import version as _get_version
from pathlib import Path
from typing import Optional

import click
from loguru import logger

from fabric_playlists.config import load_config, init_config, get_config_path
from fabric_playlists.scanner import scan_all_directories
from fabric_playlists.models import Playlist
from fabric_playlists.playlist import write_playlist


def setup_logging(level: str = "INFO") -> None:
    """Configure loguru for CLI output."""
    logger.remove()
    logger.add(
        sys.stderr,
        level=level,
        format=(
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
            "<level>{message}</level>"
        ),
        colorize=True,
    )


@click.group()
@click.option("--verbose", "-v", is_flag=True, help="Enable debug logging.")
@click.option("--config", "config_path", type=click.Path(exists=True, dir_okay=False),
              help="Path to TOML config file.")
@click.pass_context
def main(ctx: click.Context, verbose: bool, config_path: Optional[str]) -> None:
    """Manage M3U playlists for Fabric music directories.

    Configuration is loaded from (in precedence order):
      1. CLI flags (--source, --dest)
      2. Environment variables (FABRIC_SOURCE, FABRIC_DEST, FABRIC_LOG_LEVEL)
      3. TOML config file (~/.config/fabric-playlists/config.toml)
      4. Hardcoded defaults
    """
    cfg = load_config(Path(config_path) if config_path else None)
    if verbose:
        cfg.log_level = "DEBUG"
    setup_logging(cfg.log_level)
    ctx.obj = cfg
    logger.debug(f"Config loaded: source={cfg.source}, dest={cfg.dest}")


@main.command()
@click.option("--source", "-s", default=None,
              help="Source directory containing Fabric subdirectories.")
@click.option("--dest", "-d", default=None,
              help="Destination directory for generated M3U files.")
@click.option("--convert-to-m4a", is_flag=True, default=False,
              help="Transcode non-M4A tracks to M4A (requires ffmpeg).")
@click.pass_obj
def generate(cfg, source, dest, convert_to_m4a):
    """Scan Fabric directories and generate M3U playlists.

    With --convert-to-m4a, non-M4A tracks are transcoded to M4A (AAC 256kbps)
    and the playlist references the converted files. Requires ffmpeg.

    Flow:
      1. Walk directories → collect audio files
      2. Dedupe by stem, prefer .m4a (built into scan_directory)
      3. If --convert-to-m4a: transcode non-.m4a → update track paths
      4. Write playlist
    """
    source = Path(source or cfg.source)
    dest = Path(dest or cfg.dest)

    if not source.is_dir():
        raise click.ClickException(
            f"Source directory not found: {source}\n"
            f"Set via --source flag, FABRIC_SOURCE env var, or config.toml."
        )

    logger.info(f"Scanning: {source}")
    results = scan_all_directories(source)

    if not results:
        logger.warning("No directories with audio files found.")
        return

    count = 0
    for name, tracks in results:
        playlist = Playlist(name=name, tracks=tracks)

        if convert_to_m4a:
            from fabric_playlists.converter import convert_playlist_tracks
            try:
                logger.info(f"Converting tracks for '{name}' to M4A...")
                playlist = convert_playlist_tracks(playlist, source, dest)
            except RuntimeError as e:
                raise click.ClickException(str(e))

        filepath = write_playlist(playlist, dest)
        suffix = " (converted to M4A)" if convert_to_m4a else ""
        logger.success(f"  {filepath} — {len(playlist.tracks)} tracks{suffix}")
        count += 1

    logger.info(f"Generated {count} playlist(s) in {dest}")


@main.command()
@click.option("--dest", "-d", default=None,
              help="Directory containing generated playlists.")
@click.pass_obj
def list(cfg, dest):
    """List all generated playlists."""
    from fabric_playlists.playlist import list_playlists as list_pls

    dest = Path(dest or cfg.dest)
    playlists = list_pls(dest)

    if not playlists:
        click.echo(f"No playlists found in {dest}")
        return

    click.echo(f"Playlists in {dest}:")
    for p in playlists:
        click.echo(f"  {p.name} — {p.track_count} tracks")


@main.command()
@click.option("--force", "-f", is_flag=True, help="Overwrite existing config.")
def init(force):
    """Initialize: create config dir and default config.toml, then show config."""
    target = get_config_path()
    if target.exists() and not force:
        click.echo(f"Config already exists: {target}")
        click.echo("Use --force to overwrite.")
        return
    cfg = init_config(target)
    click.echo(f"Config created: {target}")
    click.echo(f"  source = {cfg.source}")
    click.echo(f"  dest   = {cfg.dest}")


@main.command()
def version():
    """Show the installed version."""
    click.echo(_get_version("fabric-playlists"))


if __name__ == "__main__":
    main()
```

**Step 4: Run test to verify pass**

```bash
cd fabric-playlists && python -m pytest tests/test_cli.py -v
```
Expected: PASS (at least 3 tests).

**Step 5: Commit**

```bash
git add fabric-playlists/src/fabric_playlists/cli.py fabric-playlists/tests/test_cli.py
git commit -m "feat: wire up generate and list CLI commands"
```

---

### Task 6: Add remaining CLI commands (validate, info, delete)

**Objective:** Implement `validate` (check file paths exist relative to source), `info` (show playlist details), and `delete` (remove a playlist file).

**Files:**
- Modify: `fabric-playlists/src/fabric_playlists/cli.py`
- Modify: `fabric-playlists/tests/test_cli.py` (add tests for new commands)

**Step 1: Write failing tests**

Add to `test_cli.py`:

```python
class TestListCommand:
    def test_lists_playlists(self, runner, temp_music_dir, tmp_path):
        dest = tmp_path / "playlists"
        # Generate first
        runner.invoke(main, ["generate", "--source", str(temp_music_dir),
                             "--dest", str(dest)])
        result = runner.invoke(main, ["list", "--dest", str(dest)])
        assert result.exit_code == 0
        assert "FABRICLIVE_72" in result.output


class TestInfoCommand:
    def test_shows_playlist_info(self, runner, temp_music_dir, tmp_path):
        dest = tmp_path / "playlists"
        runner.invoke(main, ["generate", "--source", str(temp_music_dir),
                             "--dest", str(dest)])
        result = runner.invoke(main, ["info", "FABRICLIVE_72",
                                      "--dest", str(dest)])
        assert result.exit_code == 0
        assert "FABRICLIVE_72" in result.output
        assert "tracks" in result.output.lower()

    def test_info_missing_playlist(self, runner, tmp_path):
        dest = tmp_path / "playlists"
        result = runner.invoke(main, ["info", "nonexistent",
                                      "--dest", str(dest)])
        assert result.exit_code != 0


class TestDeleteCommand:
    def test_deletes_playlist(self, runner, temp_music_dir, tmp_path):
        dest = tmp_path / "playlists"
        runner.invoke(main, ["generate", "--source", str(temp_music_dir),
                             "--dest", str(dest)])
        assert (dest / "FABRICLIVE_72.m3u").exists()

        result = runner.invoke(main, ["delete", "FABRICLIVE_72",
                                      "--dest", str(dest)])
        assert result.exit_code == 0
        assert not (dest / "FABRICLIVE_72.m3u").exists()

    def test_delete_missing_playlist(self, runner, tmp_path):
        result = runner.invoke(main, ["delete", "nonexistent"])
        assert result.exit_code != 0
```

**Step 2: Run test to verify failure**

```bash
cd fabric-playlists && python -m pytest tests/test_cli.py -v
```
Expected: FAIL — Unknown command 'info' (or similar).

**Step 3: Write minimal implementation**

Add these commands to `cli.py`:

```python
@main.command()
@click.argument("name")
@click.option("--dest", "-d", default=None)
@click.pass_obj
def info(cfg, name, dest):
    """Show details about a specific playlist."""
    from fabric_playlists.playlist import read_playlist

    dest = Path(dest or cfg.dest)
    safe_name = _safe_filename(name)
    filepath = dest / f"{safe_name}.m3u"

    playlist = read_playlist(filepath)
    if playlist is None:
        raise click.ClickException(
            f"Playlist '{name}' not found in {dest}"
        )

    click.echo(f"Name:   {playlist.name}")
    click.echo(f"Tracks: {playlist.track_count}")
    click.echo(f"File:   {filepath}")
    click.echo("\nTracks:")
    for i, track in enumerate(playlist.tracks, 1):
        click.echo(f"  {i:3d}. {track.relative_path}")


@main.command()
@click.argument("name")
@click.option("--dest", "-d", default=None)
@click.option("--source", "-s", default=None,
              help="Base source directory (for validating paths).")
@click.pass_obj
def validate(cfg, name, dest, source):
    """Check that playlist entries point to real files.

    Requires --source if tracks use relative paths.
    """
    from fabric_playlists.playlist import read_playlist

    dest = Path(dest or cfg.dest)
    source_dir = Path(source) if source else Path(cfg.source) if cfg.source else None

    safe_name = _safe_filename(name)
    filepath = dest / f"{safe_name}.m3u"

    playlist = read_playlist(filepath)
    if playlist is None:
        raise click.ClickException(
            f"Playlist '{name}' not found in {dest}"
        )

    if not source_dir or not source_dir.is_dir():
        raise click.ClickException(
            "Validation requires --source (base music directory)."
        )

    missing = []
    found = 0
    for track in playlist.tracks:
        full_path = source_dir / name / track.relative_path
        if full_path.exists():
            found += 1
        else:
            missing.append(track.relative_path)

    if missing:
        click.echo(click.style(
            f"VALIDATION FAILED: {len(missing)}/{len(playlist.tracks)} paths missing",
            fg="red"
        ))
        for path in missing:
            click.echo(f"  MISSING: {path}")
        raise click.ClickException("Validation failed.")
    else:
        click.echo(click.style(
            f"VALIDATION PASSED: {found}/{len(playlist.tracks)} paths exist",
            fg="green"
        ))


@main.command()
@click.argument("name")
@click.option("--dest", "-d", default=None)
@click.confirmation_option(prompt="Are you sure you want to delete this playlist?")
@click.pass_obj
def delete(cfg, name, dest):
    """Remove a playlist file."""
    from fabric_playlists.playlist import delete_playlist as rm_playlist

    dest = Path(dest or cfg.dest)
    success = rm_playlist(name, dest)

    if success:
        click.echo(f"Deleted playlist: {name}")
    else:
        raise click.ClickException(
            f"Playlist '{name}' not found in {dest}"
        )
```

**Step 4: Run test to verify pass**

```bash
cd fabric-playlists && python -m pytest tests/test_cli.py -v
```
Expected: PASS (all cli tests).

**Step 5: Commit**

```bash
git add fabric-playlists/src/fabric_playlists/cli.py fabric-playlists/tests/test_cli.py
git commit -m "feat: add validate, info, and delete CLI commands"
```

---

### Task 7: Finalize — README, edge cases, and integration smoke test

**Objective:** Write README, handle edge cases (empty source, unreadable dirs), and do a full integration smoke test.

**Files:**
- Create: `fabric-playlists/README.md`
- Modify: `fabric-playlists/src/fabric_playlists/scanner.py` (edge case: permission errors)
- Modify: `fabric-playlists/tests/test_cli.py` (integration smoke test)

**Step 1: Write README**

```markdown
# Fabric Playlists

Generate and manage M3U playlists for Fabric music directories.

## Install

```bash
cd fabric-playlists
pip install .
```

For development (includes lint, typecheck, test tooling):

```bash
pip install ".[dev]"
```

## Quick Start

```bash
# 1. Bootstrap your config file (creates ~/.config/fabric-playlists/config.toml)
fabric-playlists init

# 2. Edit it if needed, or set env vars
export FABRIC_SOURCE="/path/to/Fabric"
export FABRIC_DEST="/path/to/playlists"

# 3. Generate playlists
fabric-playlists generate

# 4. Enable verbose logging
fabric-playlists --verbose generate
```

## Usage

```bash
# Generate playlists
fabric-playlists generate --source /path/to/Fabric --dest /path/to/playlists

# Generate and transcode non-M4A tracks to M4A (requires ffmpeg)
fabric-playlists generate --convert-to-m4a

# List playlists
fabric-playlists list --dest /path/to/playlists

# Show playlist details
fabric-playlists info "FABRICLIVE_72" --dest /path/to/playlists

# Validate playlist paths
fabric-playlists validate "FABRICLIVE_72" --dest /path/to/playlists --source /path/to/Fabric

# Delete a playlist
fabric-playlists delete "FABRICLIVE_72" --dest /path/to/playlists
```

## Configuration

Settings are loaded in this order (later overrides earlier):

1. **Hardcoded defaults** — `/mnt/synologynas/Raw Music/Fabric` → `/mnt/synologynas/Raw Music/playlists`
2. **TOML config file** — `~/.config/fabric-playlists/config.toml` (Linux) or the platform-appropriate config directory. Create it with `fabric-playlists init`.
3. **Environment variables** — `FABRIC_SOURCE`, `FABRIC_DEST`, `FABRIC_LOG_LEVEL`
4. **CLI flags** — `--source`, `--dest` on each command

Example `config.toml`:

```toml
source = "/mnt/synologynas/Raw Music/Fabric"
dest = "/mnt/synologynas/Raw Music/playlists"
log_level = "INFO"
```

Set environment variables to override:

```bash
export FABRIC_SOURCE="/mnt/synologynas/Raw Music/Fabric"
export FABRIC_DEST="/mnt/synologynas/Raw Music/playlists"
```

Then commands work without flags:

```bash
fabric-playlists generate
fabric-playlists list
```

## Development

All quality and test commands run through `poethepoet`:

```bash
poe lint        # ruff check
poe lint-fix    # ruff check --fix
poe typecheck   # ty (strict mode)
poe test        # pytest -v
poe qa          # lint + typecheck + test (all three)
```

Run `poe qa` before committing to catch everything at once.

## Project Layout

```
src/fabric_playlists/
├── cli.py          Click CLI (generate, list, info, validate, delete)
├── scanner.py      Directory walking + m4a dedup
├── playlist.py     M3U read/write/list/delete
├── models.py       Track, Playlist dataclasses
└── converter.py    ffmpeg .m4a transcoding
tests/
├── test_cli.py
├── test_scanner.py
├── test_playlist.py
├── test_converter.py
└── conftest.py     temp music dir fixtures
```
```

**Step 2: Add edge case handling in scanner.py**

In `scan_directory`, wrap `os.walk` in a try/except for PermissionError:

```python
def scan_directory(dir_path: Path) -> List[Track]:
    # ... existing code ...
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
        pass  # Skip directories we can't read
    return sorted(tracks)
```

**Step 3: Add integration smoke test to test_cli.py**

```python
class TestEndToEnd:
    """Full workflow: generate → list → info → validate → delete."""

    def test_full_workflow(self, runner, temp_music_dir, tmp_path):
        dest = tmp_path / "playlists"

        # 1. Generate
        result = runner.invoke(main, [
            "generate", "--source", str(temp_music_dir),
            "--dest", str(dest),
        ])
        assert result.exit_code == 0
        assert (dest / "FABRICLIVE_72.m3u").exists()

        # 2. List
        result = runner.invoke(main, ["list", "--dest", str(dest)])
        assert result.exit_code == 0
        assert "FABRICLIVE_72" in result.output

        # 3. Info
        result = runner.invoke(main, ["info", "FABRICLIVE_72",
                                      "--dest", str(dest)])
        assert result.exit_code == 0
        assert "01 - Intro.mp3" in result.output

        # 4. Validate
        result = runner.invoke(main, [
            "validate", "FABRICLIVE_72",
            "--dest", str(dest),
            "--source", str(temp_music_dir),
        ])
        assert result.exit_code == 0
        assert "PASSED" in result.output

        # 5. Delete (skip confirmation by passing --yes)
        result = runner.invoke(main, [
            "delete", "FABRICLIVE_72",
            "--dest", str(dest),
            "--yes",
        ])
        assert result.exit_code == 0
        assert not (dest / "FABRICLIVE_72.m3u").exists()
```

**Step 4: Run all tests**

```bash
cd fabric-playlists && poe test
```
Expected: ALL tests pass (~25 tests).

**Step 5: Commit**

```bash
git add fabric-playlists/
git commit -m "docs: add README and edge-case handling; full integration test"
```

---

## Next Steps

After all 9 tasks complete, the user can:

```bash
cd fabric-playlists
pip install ".[dev]"

# Run the full QA suite (lint + typecheck + tests)
poe qa

# Bootstrap configuration
fabric-playlists init
# → creates ~/.config/fabric-playlists/config.toml

# Set env vars (optional — overrides config.toml)
export FABRIC_SOURCE="/mnt/synologynas/Raw Music/Fabric"
export FABRIC_DEST="/mnt/synologynas/Raw Music/playlists"

# Generate playlists (with verbose logging)
fabric-playlists --verbose generate

# Generate and transcode non-M4A tracks (requires ffmpeg)
fabric-playlists generate --convert-to-m4a

# List, inspect, validate, delete
fabric-playlists list
fabric-playlists info FABRICLIVE_72
fabric-playlists validate FABRICLIVE_72 --source "/mnt/synologynas/Raw Music/Fabric"
fabric-playlists delete FABRICLIVE_72
```

---

**Ready to execute using subagent-driven-development.** Shall I proceed?
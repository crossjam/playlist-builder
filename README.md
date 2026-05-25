# Playlist Builder

Generate and manage M3U playlists from directories of music files.

## Install

```bash
cd playlist-builder
pip install .
```

For development (includes lint, typecheck, test tooling):
```bash
pip install ".[dev]"
```

## Quick Start

```bash
# 1. Bootstrap your config file (creates ~/.config/playlist-builder/config.toml)
playlist-builder init

# 2. Edit it if needed, or set env vars
export FABRIC_SOURCE="/path/to/Music"
export FABRIC_DEST="/path/to/playlists"

# 3. Generate playlists
playlist-builder generate

# 4. Enable verbose logging
playlist-builder --verbose generate
```

## Usage

```bash
# Generate playlists
playlist-builder generate --source /path/to/Music --dest /path/to/playlists

# Generate and transcode non-M4A tracks to M4A (requires ffmpeg)
playlist-builder generate --convert-to-m4a

# List playlists
playlist-builder list --dest /path/to/playlists

# Show playlist details
playlist-builder info "FABRICLIVE_72" --dest /path/to/playlists

# Validate playlist paths
playlist-builder validate "FABRICLIVE_72" --dest /path/to/playlists --source /path/to/Music

# Delete a playlist
playlist-builder delete "FABRICLIVE_72" --dest /path/to/playlists
```

## Configuration

Settings are loaded in this order (later overrides earlier):

1. Hardcoded defaults
2. TOML config file — `~/.config/playlist-builder/config.toml` (Linux) or platform-appropriate. Create with `playlist-builder init`.
3. Environment variables — `FABRIC_SOURCE`, `FABRIC_DEST`, `FABRIC_LOG_LEVEL`
4. CLI flags — `--source`, `--dest` on each command

Example config.toml:
```toml
source = "/path/to/Music"
dest = "/mnt/synologynas/Raw Music/playlists"
log_level = "INFO"
```

## Development

All quality and test commands run through poethepoet:
```bash
poe lint        # ruff check
poe lint-fix    # ruff check --fix
poe typecheck   # ty (strict mode)
poe test        # pytest -v
poe qa          # lint + typecheck + test (all three)
```

## Project Layout

```
src/playlist_builder/
  cli.py          Click CLI (generate, list, info, validate, delete, init, version)
  scanner.py      Directory walking + m4a dedup
  playlist.py     M3U read/write/list/delete
  models.py       Track, Playlist dataclasses
  converter.py    ffmpeg .m4a transcoding
  config.py       TOML config via platformdirs + env overrides
tests/
  test_cli.py
  test_scanner.py
  test_playlist.py
  test_models.py
  test_converter.py
  test_config.py
  conftest.py     temp music dir fixtures
```

# AGENTS.md — playlist-builder

Instructions and conventions for agents working on this repo.

## Development Workflow

**Always run QA before committing:**
```
poe qa
```
This runs three gates: `ruff check`, `ty check --python-version 3.11 src/`, `pytest tests/ -v`. All must pass. Fix every error before the commit.

**Running poe:** Try `poe qa` first (direnv activates the venv automatically when the shell enters the project directory). If `poe` is not on PATH, fall back to `.venv/bin/python3 -m poethepoet qa`. Do not hardcode `.venv/bin/poe` — the shebang in that script breaks if the repo is moved or renamed.

**Virtualenv required:**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```
Never install into the system Python.

**Poe tasks:**
| Task | Command |
|---|---|
| `poe lint` | `ruff check src/ tests/` |
| `poe lint-fix` | `ruff check --fix src/ tests/` |
| `poe typecheck` | `ty check --python-version 3.11 src/` |
| `poe test` | `pytest tests/ -v` |
| `poe qa` | lint + typecheck + test |

The `ty` CLI is `ty check` (not `ty` alone). Flag is `--python-version 3.11` (not `--target-version py311`, not `--python-version py311`). Do not add a `[tool.ty]` section to pyproject.toml — `ty`'s config schema is unstable; use the CLI flag.

## Python Version

Target Python 3.11+. In `pyproject.toml`: `requires-python = ">=3.11"`. Ruff target: `py311`. `ty`: `--python-version 3.11`. Python 3.12 is on the host machine but 3.11 is the floor — no 3.12-only syntax (`type` parameter syntax, `@override`) without a bump.

## Code Style

- Ruff config: `target-version = "py311"`, `line-length = 100`
- Select rules: E, F, I, N, W, UP, B, SIM, C4
- Imports: stdlib first, then third-party, then local (isort via ruff I rule)
- Use `Path | None` not `Optional[Path]` (UP045)
- Use `list[T]` not `List[T]` from typing
- F-strings only when there are actual placeholders (F541)

## Commit Style

Lowercase imperative: `feat: ...`, `fix: ...`, `test: ...`, `chore: ...`

## Logging

`loguru` for all output. Configure via `setup_logging(level)` in cli.py. `--verbose`/`-v` → DEBUG. Log level default is INFO from config.
- `logger.info()` for normal progress
- `logger.success()` for completed operations
- `logger.warning()` for skippable issues
- `logger.debug()` for troubleshooting
- `logger.error()` for failures

## Configuration

Layering (highest priority first):
1. CLI flags (`--source`, `--dest`)
2. Environment variables (`FABRIC_SOURCE`, `FABRIC_DEST`, `FABRIC_LOG_LEVEL`)
3. TOML config file (`~/.config/playlist-builder/config.toml`, found via `platformdirs`)
4. Hardcoded defaults

CLI commands receive config via `@click.pass_obj` → `ctx.obj = cfg` in the group callback. Use `cfg.source`/`cfg.dest` as fallbacks when CLI flags are absent.

`_safe_filename()` lives in `config.py` — import from there, do not redefine.

## Scanner Module

Located in `src/playlist_builder/scanner.py`.

**Include patterns** (`INCLUDE_PATTERNS`): `["FABRICLIVE", "fabric presents"]` — only directories matching at least one pattern are scanned by `scan_all_directories`. Case-insensitive, substring match. Include overrides skip at the top level.

**Skip patterns** (`SKIP_PATTERNS`): `["presents", "archives"]` — applied to subdirectories during `os.walk` (not at the top level — that's handled by the include filter).

**Continuous filter**: If any track has "continuous" in its stem (substring match, case-insensitive), only those tracks are kept. If multiple continuous tracks exist, `_prompt_continuous_selection()` in cli.py presents a `rich` selection prompt. In non-interactive mode (`stdin` not a TTY), auto-selects the alphabetically first continuous file.

**Deduplication**: `_dedupe_prefer_m4a()` — when multiple files share the same stem, keep only the `.m4a` version. If no `.m4a` exists among duplicates, keep all.

**Audio extensions**: `.mp3`, `.flac`, `.wav`, `.m4a`, `.ogg`

## Converter Module

Located in `src/playlist_builder/converter.py`.

ffmpeg encoding:
- Codec: `libfdk_aac` (preferred, detected at runtime via `_detect_aac_encoder()`), fallback to built-in `aac`
- Bitrate: `128k`
- Strip non-audio streams: `-vn`
- Output: `{dest_dir}/converted/{stem}.m4a`
- Skip if `.m4a` already, skip if output exists

## CLI Commands

| Command | Purpose |
|---|---|
| `playlist-builder [--verbose] [--config PATH] generate` | Scan and create M3U files |
| `playlist-builder generate --convert-to-m4a` | Transcode non-M4A to M4A |
| `playlist-builder generate --overwrite` | Replace existing files (smart: skip if unchanged) |
| `playlist-builder list` | List all playlists |
| `playlist-builder info NAME` | Show playlist details |
| `playlist-builder validate NAME` | Check paths exist |
| `playlist-builder delete NAME` | Remove a playlist |
| `playlist-builder init` | Bootstrap config.toml |
| `playlist-builder version` | Show installed version |

## Testing

- Framework: `pytest` with `CliRunner` for CLI tests
- Key fixture: `temp_music_dir` (in `conftest.py`) — simulates Fabric folder structure with normal albums, presents dirs, archives dirs, empty dirs, nested dirs, duplicate stems, continuous files, and space-containing names
- Use `tmp_path` for isolated output directories
- Use `monkeypatch` for environment variable tests
- Tests that invoke `generate` must account for the include filter and continuous prompt (non-interactive mode auto-selects)
- ffmpeg-dependent tests: `pytest.skip("ffmpeg not installed")` if ffmpeg unavailable

## Dependencies

Runtime: `click`, `loguru`, `platformdirs`, `rich`
Dev: `poethepoet`, `ruff`, `ty`, `pytest`
Optional: system `ffmpeg` for transcoding

## Memory and Skills

- Always run `poe qa` before committing to this repo (saved to Hermes memory)
- Python 3.11 minimum for new projects (saved to Hermes memory)
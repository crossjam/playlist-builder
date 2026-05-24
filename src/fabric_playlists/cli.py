"""CLI entry point for fabric-playlists."""

import sys
from importlib.metadata import version as _get_version
from pathlib import Path

import click
from loguru import logger
from rich.prompt import Prompt

from fabric_playlists.config import _safe_filename, get_config_path, init_config, load_config
from fabric_playlists.models import Playlist
from fabric_playlists.playlist import write_playlist
from fabric_playlists.scanner import scan_all_directories


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
@click.option(
    "--verbose", "-v", is_flag=True, help="Enable debug logging."
)
@click.option(
    "--config",
    "config_path",
    type=click.Path(exists=True, dir_okay=False),
    help="Path to TOML config file.",
)
@click.pass_context
def main(ctx: click.Context, verbose: bool, config_path: str | None) -> None:
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


def _prompt_continuous_selection(tracks):
    """If multiple tracks have 'continuous' in their stem, prompt user to pick one."""
    continuous = [t for t in tracks if "continuous" in Path(t.relative_path).stem.lower()]
    if len(continuous) <= 1:
        return tracks
    if not sys.stdin.isatty():
        # Non-interactive: auto-select the first continuous file
        logger.info(f"Non-interactive mode: auto-selecting {continuous[0].relative_path}")
        return [continuous[0]]
    non_continuous = [t for t in tracks if t not in continuous]
    click.echo("\nMultiple continuous files found in directory:")
    choices = []
    for i, t in enumerate(continuous, 1):
        click.echo(f"  {i}. {t.relative_path}")
        choices.append(str(i))
    none_choice = str(len(continuous) + 1)
    click.echo(f"  {none_choice}. Keep all regular tracks (ignore continuous)")
    choices.append(none_choice)
    choice = Prompt.ask("Select", choices=choices, default="1")
    idx = int(choice) - 1
    if idx == len(continuous):
        return non_continuous
    return [continuous[idx]]


@main.command()
@click.option(
    "--source", "-s", default=None,
    help="Source directory containing Fabric subdirectories.",
)
@click.option(
    "--dest", "-d", default=None,
    help="Destination directory for generated M3U files.",
)
@click.option(
    "--convert-to-m4a", is_flag=True, default=False,
    help="Transcode non-M4A tracks to M4A (requires ffmpeg).",
)
@click.option(
    "--overwrite", is_flag=True, default=False,
    help="Overwrite existing M3U files instead of skipping them.",
)
@click.pass_obj
def generate(cfg, source, dest, convert_to_m4a, overwrite):
    """Scan Fabric directories and generate M3U playlists."""
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

    from fabric_playlists.config import _safe_filename as safe_fn

    count = 0
    skipped = 0
    for name, tracks in results:
        playlist = Playlist(name=name, tracks=tracks)

        # Handle continuous file selection
        playlist = Playlist(name=name, tracks=_prompt_continuous_selection(playlist.tracks))

        if convert_to_m4a:
            from fabric_playlists.converter import convert_playlist_tracks

            try:
                logger.info(f"Converting tracks for '{name}' to M4A...")
                playlist = convert_playlist_tracks(playlist, source, dest)
            except RuntimeError as e:
                raise click.ClickException(str(e)) from e

        out_path = dest / f"{safe_fn(name)}.m3u"
        if out_path.exists():
            if not overwrite:
                logger.warning(
                    f"  Skipping {out_path}"
                    f" (already exists, use --overwrite to replace)"
                )
                skipped += 1
                continue
            # Smart overwrite: only write if content actually changed
            new_content = playlist.to_m3u()
            try:
                old_content = out_path.read_text()
            except OSError:
                old_content = ""
            if new_content == old_content:
                logger.info(f"  {out_path} unchanged, skipping")
                skipped += 1
                continue
            logger.info(f"  Overwriting {out_path} (content changed)")

        filepath = write_playlist(playlist, dest)
        suffix = " (converted to M4A)" if convert_to_m4a else ""
        logger.success(f"  {filepath} — {len(playlist.tracks)} tracks{suffix}")
        count += 1

    if skipped:
        logger.info(f"Skipped {skipped} existing playlist(s)")
    logger.info(f"Generated {count} playlist(s) in {dest}")


@main.command()
@click.option(
    "--dest", "-d", default=None,
    help="Directory containing generated playlists.",
)
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
@click.option(
    "--force", "-f", is_flag=True, help="Overwrite existing config."
)
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
        raise click.ClickException(f"Playlist '{name}' not found in {dest}")
    click.echo(f"Name:   {playlist.name}")
    click.echo(f"Tracks: {playlist.track_count}")
    click.echo(f"File:   {filepath}")
    click.echo("\nTracks:")
    for i, track in enumerate(playlist.tracks, 1):
        click.echo(f"  {i:3d}. {track.relative_path}")


@main.command()
@click.argument("name")
@click.option("--dest", "-d", default=None)
@click.option("--source", "-s", default=None, help="Base source directory (for validating paths).")
@click.pass_obj
def validate(cfg, name, dest, source):
    """Check that playlist entries point to real files."""
    from fabric_playlists.playlist import read_playlist
    dest = Path(dest or cfg.dest)
    source_dir = Path(source) if source else Path(cfg.source) if cfg.source else None
    safe_name = _safe_filename(name)
    filepath = dest / f"{safe_name}.m3u"
    playlist = read_playlist(filepath)
    if playlist is None:
        raise click.ClickException(f"Playlist '{name}' not found in {dest}")
    if not source_dir or not source_dir.is_dir():
        raise click.ClickException("Validation requires --source (base music directory).")
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
            fg="red",
        ))
        for path in missing:
            click.echo(f"  MISSING: {path}")
        raise click.ClickException("Validation failed.")
    else:
        click.echo(click.style(
            f"VALIDATION PASSED: {found}/{len(playlist.tracks)} paths exist",
            fg="green",
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
        raise click.ClickException(f"Playlist '{name}' not found in {dest}")


if __name__ == "__main__":
    main()

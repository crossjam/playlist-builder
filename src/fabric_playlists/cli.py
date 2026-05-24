"""Click CLI entry point for fabric-playlists."""

from importlib.metadata import version as _get_version

import click


@click.group()
def main() -> None:
    """fabric-playlists — generate and manage M3U playlists for Fabric music directories."""
    pass


@main.command()
def generate() -> None:
    """Generate playlists from a music directory."""
    click.echo("Not implemented")


@main.command()
def list() -> None:
    """List available playlists."""
    click.echo("Not implemented")


@main.command()
def version() -> None:
    """Show the installed version."""
    click.echo(_get_version("fabric-playlists"))

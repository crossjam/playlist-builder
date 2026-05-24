"""Click CLI entry point for fabric-playlists."""

import click

from importlib.metadata import version


@click.group()
def main() -> None:
    """fabric-playlists — generate and manage M3U playlists for Fabric music directories."""
    pass


@main.command()
def generate() -> None:
    """Generate playlists from a music directory."""
    click.echo("Not implemented")


@main.command()
def list() -> None:  # noqa: A001
    """List available playlists."""
    click.echo("Not implemented")


@main.command()
def version_cmd() -> None:
    """Show the current version."""
    click.echo(version("fabric-playlists"))

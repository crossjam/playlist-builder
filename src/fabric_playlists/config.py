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

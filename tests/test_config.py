"""Tests for configuration module."""

from fabric_playlists.config import (
    AppConfig,
    get_config_dir,
    get_config_path,
    init_config,
    load_config,
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
        assert cfg.dest == "/mnt/synologynas/Raw Music/playlists"

    def test_with_env_overrides_applies_env_vars(self, monkeypatch):
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
        assert cfg.dest == "/mnt/synologynas/Raw Music/playlists"


class TestLoadConfig:
    def test_load_config_merges_toml_and_env(self, monkeypatch, tmp_path):
        toml_path = tmp_path / "config.toml"
        toml_path.write_text('source = "/file/source"\ndest = "/file/dest"\n')
        monkeypatch.setenv("FABRIC_SOURCE", "/env/source")
        cfg = load_config(toml_path)
        assert cfg.source == "/env/source"
        assert cfg.dest == "/file/dest"


class TestInitConfig:
    def test_creates_config_file_if_missing(self, tmp_path):
        target = tmp_path / "config.toml"
        _ = init_config(target)
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

"""Tests for configuration system."""

import pytest

from taskng.config.settings import Config, reset_config


@pytest.fixture(autouse=True)
def reset_singleton():
    """Reset config singleton before each test."""
    reset_config()
    yield
    reset_config()


class TestConfig:
    """Tests for Config class."""

    def test_default_values(self, tmp_path):
        """Should load sensible default values when no config file.

        Defaults are chosen for best out-of-box experience:
        - ui.color=True: Modern terminals support colors
        - ui.unicode=True: Checkmarks and symbols improve readability
        - default.command="next": Show high-urgency tasks by default
          (Taskwarrior convention, most useful view for new users)
        """
        config = Config(tmp_path / "config.toml")

        # Color enabled by default (most terminals support it)
        assert config.get("ui.color") is True
        # Unicode enabled for visual task indicators (✓, ⚠, etc)
        assert config.get("ui.unicode") is True
        # "next" shows highest urgency tasks first (Taskwarrior convention)
        assert config.get("default.command") == "next"

    def test_get_nested_value(self, tmp_path):
        """Should get nested values with dot notation."""
        config = Config(tmp_path / "config.toml")

        assert config.get("report.list.columns") is not None
        assert "id" in config.get("report.list.columns")

    def test_get_missing_key(self, tmp_path):
        """Should return default for missing key."""
        config = Config(tmp_path / "config.toml")

        assert config.get("nonexistent") is None
        assert config.get("nonexistent", "default") == "default"

    def test_set_value(self, tmp_path):
        """Should set values with dot notation."""
        config = Config(tmp_path / "config.toml")

        config.set("ui.color", False)
        assert config.get("ui.color") is False

    def test_set_nested_creates_path(self, tmp_path):
        """Should create nested path when setting."""
        config = Config(tmp_path / "config.toml")

        config.set("custom.nested.value", "test")
        assert config.get("custom.nested.value") == "test"

    def test_load_from_file(self, tmp_path):
        """Should load config from TOML file."""
        config_file = tmp_path / "config.toml"
        config_file.write_text(
            """
[ui]
color = false

[data]
location = "/custom/path"
"""
        )

        config = Config(config_file)

        assert config.get("ui.color") is False
        assert config.get("data.location") == "/custom/path"
        # Defaults still loaded
        assert config.get("ui.unicode") is True

    def test_load_env_variables(self, tmp_path, monkeypatch):
        """Should load TASKNG_* environment variables."""
        monkeypatch.setenv("TASKNG_UI__COLOR", "false")
        monkeypatch.setenv("TASKNG_DATA__LOCATION", "/env/path")

        config = Config(tmp_path / "config.toml")

        assert config.get("ui.color") is False
        assert config.get("data.location") == "/env/path"

    def test_env_overrides_file(self, tmp_path, monkeypatch):
        """Environment variables should override file config."""
        config_file = tmp_path / "config.toml"
        config_file.write_text("[ui]\ncolor = true")

        monkeypatch.setenv("TASKNG_UI__COLOR", "false")

        config = Config(config_file)

        assert config.get("ui.color") is False

    def test_convert_boolean_values(self, tmp_path, monkeypatch):
        """Should convert string booleans."""
        monkeypatch.setenv("TASKNG_TEST__TRUE", "true")
        monkeypatch.setenv("TASKNG_TEST__FALSE", "false")
        monkeypatch.setenv("TASKNG_TEST__YES", "yes")
        monkeypatch.setenv("TASKNG_TEST__NO", "no")

        config = Config(tmp_path / "config.toml")

        assert config.get("test.true") is True
        assert config.get("test.false") is False
        assert config.get("test.yes") is True
        assert config.get("test.no") is False

    def test_convert_integer_values(self, tmp_path, monkeypatch):
        """Should convert string integers."""
        monkeypatch.setenv("TASKNG_TEST__NUMBER", "42")

        config = Config(tmp_path / "config.toml")

        assert config.get("test.number") == 42

    def test_save_config(self, tmp_path):
        """Should save config to file."""
        config_file = tmp_path / "config.toml"
        config = Config(config_file)

        config.set("ui.color", False)
        config.set("custom.value", "test")
        config.save()

        assert config_file.exists()
        content = config_file.read_text()
        assert "color = false" in content

    def test_data_location_property(self, tmp_path):
        """Should return data location as Path."""
        config = Config(tmp_path / "config.toml")

        location = config.data_location
        assert isinstance(location, type(tmp_path))

    def test_color_enabled_property(self, tmp_path):
        """Should return color enabled status."""
        config = Config(tmp_path / "config.toml")

        assert config.color_enabled is True

        config.set("ui.color", False)
        assert config.color_enabled is False

    def test_merge_nested_dicts(self, tmp_path):
        """Should merge nested dictionaries properly."""
        config_file = tmp_path / "config.toml"
        config_file.write_text(
            """
[report.list]
columns = ["id", "description"]
"""
        )

        config = Config(config_file)

        # Should override columns but keep sort
        assert config.get("report.list.columns") == ["id", "description"]
        assert config.get("report.list.sort") == ["urgency-"]

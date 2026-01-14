"""Integration tests for init command."""

from typer.testing import CliRunner

from taskng.cli.main import app

runner = CliRunner()


class TestInitCommand:
    """Test task-ng init command."""

    def test_init_creates_taskng_directory(self, tmp_path, monkeypatch):
        """Should create .taskng directory in current directory."""
        monkeypatch.chdir(tmp_path)
        result = runner.invoke(app, ["init"])

        assert result.exit_code == 0
        local_dir = tmp_path / ".taskng"
        assert local_dir.exists()
        assert local_dir.is_dir()

    def test_init_creates_config_file(self, tmp_path, monkeypatch):
        """Should create config.toml file."""
        monkeypatch.chdir(tmp_path)
        result = runner.invoke(app, ["init"])

        assert result.exit_code == 0
        config_file = tmp_path / ".taskng" / "config.toml"
        assert config_file.exists()
        content = config_file.read_text()
        assert "Task-NG Configuration" in content

    def test_init_creates_database(self, tmp_path, monkeypatch):
        """Should create task.db database file."""
        monkeypatch.chdir(tmp_path)
        result = runner.invoke(app, ["init"])

        assert result.exit_code == 0
        db_file = tmp_path / ".taskng" / "task.db"
        assert db_file.exists()
        assert db_file.stat().st_size > 0

    def test_init_shows_success_message(self, tmp_path, monkeypatch):
        """Should show success message with paths."""
        monkeypatch.chdir(tmp_path)
        result = runner.invoke(app, ["init"])

        assert result.exit_code == 0
        assert "Initialized task-ng" in result.stdout
        assert ".taskng" in result.stdout
        assert "Config:" in result.stdout
        assert "Database:" in result.stdout

    def test_init_fails_when_directory_exists(self, tmp_path, monkeypatch):
        """Should fail when .taskng directory already exists."""
        monkeypatch.chdir(tmp_path)
        local_dir = tmp_path / ".taskng"
        local_dir.mkdir()

        result = runner.invoke(app, ["init"])

        assert result.exit_code == 1
        assert "Error:" in result.stdout
        assert "already exists" in result.stdout
        assert "--force" in result.stdout

    def test_init_with_force_flag(self, tmp_path, monkeypatch):
        """Should succeed with --force when directory exists."""
        monkeypatch.chdir(tmp_path)
        local_dir = tmp_path / ".taskng"
        local_dir.mkdir()

        result = runner.invoke(app, ["init", "--force"])

        assert result.exit_code == 0
        assert "Initialized task-ng" in result.stdout

    def test_init_with_force_short_flag(self, tmp_path, monkeypatch):
        """Should support -f short flag for --force."""
        monkeypatch.chdir(tmp_path)
        local_dir = tmp_path / ".taskng"
        local_dir.mkdir()

        result = runner.invoke(app, ["init", "-f"])

        assert result.exit_code == 0
        assert "Initialized task-ng" in result.stdout

    def test_init_overwrites_config_with_force(self, tmp_path, monkeypatch):
        """Should overwrite existing config with --force."""
        monkeypatch.chdir(tmp_path)
        local_dir = tmp_path / ".taskng"
        local_dir.mkdir()
        config_file = local_dir / "config.toml"
        config_file.write_text("old config")

        result = runner.invoke(app, ["init", "--force"])

        assert result.exit_code == 0
        new_content = config_file.read_text()
        assert "Task-NG Configuration" in new_content
        assert "old config" not in new_content

    def test_init_reinitializes_database_with_force(self, tmp_path, monkeypatch):
        """Should reinitialize database with --force."""
        monkeypatch.chdir(tmp_path)
        local_dir = tmp_path / ".taskng"
        local_dir.mkdir()
        db_file = local_dir / "task.db"
        db_file.write_bytes(b"")
        old_size = db_file.stat().st_size

        result = runner.invoke(app, ["init", "--force"])

        assert result.exit_code == 0
        assert db_file.exists()
        new_size = db_file.stat().st_size
        assert new_size > old_size

    def test_init_multiple_times_fails_without_force(self, tmp_path, monkeypatch):
        """Should fail on second init without --force."""
        monkeypatch.chdir(tmp_path)
        # First init succeeds
        result1 = runner.invoke(app, ["init"])
        assert result1.exit_code == 0

        # Second init fails
        result2 = runner.invoke(app, ["init"])
        assert result2.exit_code == 1
        assert "already exists" in result2.stdout

    def test_init_then_add_task(self, tmp_path, monkeypatch):
        """Should be able to add tasks after init."""
        monkeypatch.chdir(tmp_path)
        # Initialize
        result1 = runner.invoke(app, ["init"])
        assert result1.exit_code == 0

        # Add task in the initialized directory
        result2 = runner.invoke(app, ["add", "Test task"])
        assert result2.exit_code == 0
        assert "Created task" in result2.stdout

    def test_init_then_list_tasks(self, tmp_path, monkeypatch):
        """Should show empty list after init."""
        monkeypatch.chdir(tmp_path)
        # Initialize
        result1 = runner.invoke(app, ["init"])
        assert result1.exit_code == 0

        # List tasks should show empty
        result2 = runner.invoke(app, ["list"])
        assert result2.exit_code == 0
        assert "No matching tasks" in result2.stdout

    def test_init_creates_isolated_environment(self, tmp_path, temp_db, monkeypatch):
        """Should create isolated environment, not affecting global tasks."""
        # Create a task in global database
        from taskng.core.models import Task, TaskStatus
        from taskng.storage.repository import TaskRepository

        repo = TaskRepository(temp_db)
        task = Task(description="Global task", status=TaskStatus.PENDING)
        repo.add(task)

        # Initialize local directory
        monkeypatch.chdir(tmp_path)
        result = runner.invoke(app, ["init"])
        assert result.exit_code == 0

        # List in local directory should be empty (not showing global task)
        result2 = runner.invoke(app, ["list"])
        assert result2.exit_code == 0
        assert "Global task" not in result2.stdout

    def test_init_in_subdirectory(self, tmp_path, monkeypatch):
        """Should work in subdirectories."""
        subdir = tmp_path / "project" / "subdir"
        subdir.mkdir(parents=True)

        monkeypatch.chdir(subdir)
        result = runner.invoke(app, ["init"])

        assert result.exit_code == 0
        local_dir = subdir / ".taskng"
        assert local_dir.exists()
        assert (local_dir / "config.toml").exists()
        assert (local_dir / "task.db").exists()

    def test_init_help_message(self):
        """Should show help message."""
        result = runner.invoke(app, ["init", "--help"])

        assert result.exit_code == 0
        assert "init" in result.stdout.lower()
        assert "--force" in result.stdout or "-f" in result.stdout

    def test_init_paths_in_output(self, tmp_path, monkeypatch):
        """Should show full paths in success message."""
        monkeypatch.chdir(tmp_path)
        result = runner.invoke(app, ["init"])

        assert result.exit_code == 0
        # Check that actual paths are shown
        assert "config.toml" in result.stdout
        assert "task.db" in result.stdout

    def test_init_config_is_comprehensive(self, tmp_path, monkeypatch):
        """Should create comprehensive config with all sections."""
        monkeypatch.chdir(tmp_path)
        result = runner.invoke(app, ["init"])

        assert result.exit_code == 0
        config_file = tmp_path / ".taskng" / "config.toml"
        content = config_file.read_text()

        # Verify file is substantial (not just a comment)
        assert len(content) > 1000, "Config should be comprehensive"

        # Verify major section headers are present
        assert "## Data Storage" in content
        assert "## Default Behavior" in content
        assert "## UI Settings" in content
        assert "## Color Scheme" in content
        assert "## Calendar Settings" in content
        assert "## Urgency Calculation" in content
        assert "## Report Definitions" in content
        assert "## Board Definitions" in content
        assert "## Context Definitions" in content

    def test_init_config_contains_all_key_settings(self, tmp_path, monkeypatch):
        """Should document all key configuration options."""
        monkeypatch.chdir(tmp_path)
        result = runner.invoke(app, ["init"])

        assert result.exit_code == 0
        config_file = tmp_path / ".taskng" / "config.toml"
        content = config_file.read_text()

        # Verify key settings are documented
        assert "[data]" in content
        assert "location =" in content
        assert "[default]" in content
        assert "command =" in content
        assert "[defaults]" in content
        assert "sort =" in content
        assert "[ui]" in content
        assert "color =" in content
        assert "unicode =" in content
        assert "[color.due]" in content
        assert "[color.priority]" in content
        assert "[urgency]" in content
        assert "priority =" in content
        assert "[report.list]" in content
        assert "[board.default]" in content
        assert "[calendar]" in content
        assert "weekstart =" in content

    def test_init_config_has_commented_defaults(self, tmp_path, monkeypatch):
        """Should have most settings commented out by default."""
        monkeypatch.chdir(tmp_path)
        result = runner.invoke(app, ["init"])

        assert result.exit_code == 0
        config_file = tmp_path / ".taskng" / "config.toml"
        content = config_file.read_text()

        # Count commented lines vs uncommented
        lines = content.split("\n")
        comment_lines = sum(1 for line in lines if line.strip().startswith("#"))
        non_empty_lines = sum(1 for line in lines if line.strip())

        # Most lines should be comments or documentation
        assert comment_lines > non_empty_lines * 0.7, "Most content should be commented"

    def test_init_config_has_valid_structure(self, tmp_path, monkeypatch):
        """Should have well-structured config template."""
        monkeypatch.chdir(tmp_path)
        result = runner.invoke(app, ["init"])

        assert result.exit_code == 0
        config_file = tmp_path / ".taskng" / "config.toml"
        content = config_file.read_text()

        # Verify file has proper structure with section headers and settings
        assert "[data]" in content
        assert "[default]" in content
        assert "[ui]" in content
        assert "Task-NG Configuration" in content

        # Verify TOML section syntax is present (even if commented)
        assert content.count("[") > 10, "Should have multiple TOML sections"
        assert content.count("=") > 20, "Should have many configuration options"

    def test_init_config_contains_helpful_comments(self, tmp_path, monkeypatch):
        """Should include helpful inline comments explaining options."""
        monkeypatch.chdir(tmp_path)
        result = runner.invoke(app, ["init"])

        assert result.exit_code == 0
        config_file = tmp_path / ".taskng" / "config.toml"
        content = config_file.read_text()

        # Verify explanatory comments are present
        assert "Default:" in content  # Shows default values
        assert "Options:" in content  # Shows available options
        assert "Weight" in content or "weight" in content  # Explains urgency
        assert "Color" in content or "color" in content  # Explains colors
        assert "Uncomment" in content  # Instructions for users

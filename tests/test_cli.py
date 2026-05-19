from typer.testing import CliRunner

from chappe.cli import app
from chappe.config import ChappeConfig


runner = CliRunner()


def test_doctor_smoke(tmp_path):
    result = runner.invoke(app, ["doctor"], env={"CHAPPE_HOME": str(tmp_path)})
    assert result.exit_code == 0
    assert '"version":' in result.stdout
    assert '"setup_complete":' in result.stdout


def test_no_args_shows_onboarding(tmp_path):
    result = runner.invoke(app, [], env={"CHAPPE_HOME": str(tmp_path)})
    assert result.exit_code == 0
    assert '"setup_steps":' in result.stdout
    assert '"agent_guided_setup":' in result.stdout
    assert '"id": "telegram_api_id"' in result.stdout
    assert '"id": "telegram_phone"' in result.stdout
    assert "chappe setup --api-id" in result.stdout
    assert "my.telegram.org/apps" in result.stdout


def test_onboard_channel_tails_setup_command(tmp_path):
    result = runner.invoke(
        app,
        ["onboard", "--channel", "@nn_for_science"],
        env={"CHAPPE_HOME": str(tmp_path)},
    )
    assert result.exit_code == 0
    assert "chappe setup --api-id <id> --api-hash <hash> --channel @nn_for_science" in result.stdout
    assert "chappe sync @nn_for_science --limit 100 --comments" in result.stdout


def test_config_init_smoke(tmp_path):
    result = runner.invoke(app, ["config", "init"], env={"CHAPPE_HOME": str(tmp_path)})
    assert result.exit_code == 0
    assert (tmp_path / ".config" / "chappe" / "config.toml").exists()


def test_setup_writes_complete_config(tmp_path):
    result = runner.invoke(
        app,
        [
            "setup",
            "--api-id",
            "123",
            "--api-hash",
            "hash",
            "--channel",
            "@nn_for_science",
        ],
        env={"CHAPPE_HOME": str(tmp_path)},
    )
    assert result.exit_code == 0
    config_path = tmp_path / ".config" / "chappe" / "config.toml"
    text = config_path.read_text()
    assert 'api_id = "123"' in text
    assert 'default_channel = "@nn_for_science"' in text


def test_setup_reads_credentials_from_environment(tmp_path):
    result = runner.invoke(
        app,
        ["setup", "--channel", "@nn_for_science"],
        env={
            "CHAPPE_HOME": str(tmp_path),
            "TELEGRAM_API_ID": "123",
            "TELEGRAM_API_HASH": "hash-from-env",
        },
    )
    assert result.exit_code == 0
    cfg = ChappeConfig.load(tmp_path / ".config" / "chappe" / "config.toml")
    assert cfg.telegram.api_id == "123"
    assert cfg.telegram.api_hash == "hash-from-env"
    assert cfg.defaults.default_channel == "@nn_for_science"


def test_setup_escapes_toml_strings(tmp_path):
    result = runner.invoke(
        app,
        [
            "setup",
            "--api-id",
            "123",
            "--api-hash",
            'hash"with\\chars',
            "--channel",
            '@nn_"science',
            "--tdlib-key",
            'key"with\\chars',
        ],
        env={"CHAPPE_HOME": str(tmp_path)},
    )
    assert result.exit_code == 0
    cfg = ChappeConfig.load(tmp_path / ".config" / "chappe" / "config.toml")
    assert cfg.telegram.api_hash == 'hash"with\\chars'
    assert cfg.telegram.database_encryption_key == 'key"with\\chars'
    assert cfg.defaults.default_channel == '@nn_"science'


def test_agent_list_smoke(tmp_path):
    result = runner.invoke(app, ["agent", "list"], env={"CHAPPE_HOME": str(tmp_path)})
    assert result.exit_code == 0
    assert "codex" in result.stdout


def test_agent_install_codex_places_skill_at_target_root(tmp_path):
    target = tmp_path / "codex-skill"
    result = runner.invoke(
        app,
        ["agent", "install", "codex", "--dest", str(target)],
        env={"CHAPPE_HOME": str(tmp_path)},
    )
    assert result.exit_code == 0
    assert (target / "SKILL.md").exists()
    assert (target / "AGENTS.snippet.md").exists()
    assert not (target / "chappe" / "SKILL.md").exists()

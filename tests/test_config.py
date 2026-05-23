from chappe.config import ChappeConfig, expand_env, render_config


def test_expand_env_reads_environment(monkeypatch):
    monkeypatch.setenv("SAMPLE_VALUE", "ok")
    assert expand_env("${SAMPLE_VALUE}") == "ok"


def test_config_load_uses_chappe_home(tmp_path, monkeypatch):
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "xdg-config"))
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path / "xdg-data"))
    monkeypatch.setenv("XDG_STATE_HOME", str(tmp_path / "xdg-state"))
    monkeypatch.setenv("CHAPPE_HOME", str(tmp_path))
    cfg = ChappeConfig.load()
    assert str(cfg.storage.sqlite_path).startswith(str(tmp_path))


def test_config_bot_token_from_env(tmp_path, monkeypatch):
    monkeypatch.setenv("CHAPPE_HOME", str(tmp_path))
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "123456:from-env")
    cfg = ChappeConfig.load()
    assert cfg.telegram.bot_token == "123456:from-env"


def test_config_bot_token_from_file_wins_over_env(tmp_path, monkeypatch):
    config_path = tmp_path / "config.toml"
    config_path.write_text(render_config(bot_token="123456:from-file"))
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "999:from-env")
    cfg = ChappeConfig.load(config_path)
    assert cfg.telegram.bot_token == "123456:from-file"


def test_render_config_persists_bot_token():
    text = render_config(bot_token="123456:abc")
    assert 'bot_token = "123456:abc"' in text


def test_render_config_omits_bot_token_when_absent():
    text = render_config()
    assert "bot_token" not in text

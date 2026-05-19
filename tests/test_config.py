from chappe.config import ChappeConfig, expand_env


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

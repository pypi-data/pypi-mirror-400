import os
import importlib


def test_pick_help():
    from click.testing import CliRunner
    from fcbyk.cli import cli

    r = CliRunner().invoke(cli, ["pick", "--help"])
    assert r.exit_code == 0


def test_pick_show_list_empty(monkeypatch):
    pick_cli = importlib.import_module("fcbyk.commands.pick.cli")

    monkeypatch.setattr(pick_cli, "load_json_config", lambda *a, **k: {"items": []})

    from click.testing import CliRunner

    r = CliRunner().invoke(pick_cli.pick, ["--list"])
    assert r.exit_code == 0
    assert "List is empty" in r.output


def test_pick_show_list_non_empty(monkeypatch):
    pick_cli = importlib.import_module("fcbyk.commands.pick.cli")

    monkeypatch.setattr(pick_cli, "load_json_config", lambda *a, **k: {"items": ["a", "b"]})

    from click.testing import CliRunner

    r = CliRunner().invoke(pick_cli.pick, ["--list"])
    assert r.exit_code == 0
    assert "Current items list" in r.output
    assert "1. a" in r.output
    assert "2. b" in r.output


def test_pick_clear(monkeypatch):
    pick_cli = importlib.import_module("fcbyk.commands.pick.cli")

    store = {"items": ["a"]}

    monkeypatch.setattr(pick_cli, "load_json_config", lambda *a, **k: dict(store))

    def _save(cfg, path):
        store.clear()
        store.update(cfg)

    monkeypatch.setattr(pick_cli, "save_config", _save)

    from click.testing import CliRunner

    r = CliRunner().invoke(pick_cli.pick, ["--clear"])
    assert r.exit_code == 0
    assert store["items"] == []
    assert "List cleared" in r.output


def test_pick_add_and_remove(monkeypatch):
    pick_cli = importlib.import_module("fcbyk.commands.pick.cli")

    # 用内存对象模拟 config
    store = {"items": []}

    monkeypatch.setattr(pick_cli, "load_json_config", lambda *a, **k: dict(store))

    def _save(cfg, path):
        store.clear()
        store.update(cfg)

    monkeypatch.setattr(pick_cli, "save_config", _save)

    from click.testing import CliRunner

    runner = CliRunner()

    r = runner.invoke(pick_cli.pick, ["--add", "a", "--add", "b", "--add", "a"])
    assert r.exit_code == 0
    assert store["items"] == ["a", "b"]

    r = runner.invoke(pick_cli.pick, ["--remove", "b", "--remove", "x"])
    assert r.exit_code == 0
    assert store["items"] == ["a"]


def test_pick_web_calls_start_web_server(monkeypatch):
    pick_cli = importlib.import_module("fcbyk.commands.pick.cli")

    called = {}

    monkeypatch.setattr(pick_cli, "load_json_config", lambda *a, **k: {"items": []})
    monkeypatch.setattr(pick_cli, "PickService", lambda *a, **k: object())

    def _start(port, no_browser, **kwargs):
        called.update({"port": port, "no_browser": no_browser, **kwargs})

    monkeypatch.setattr(pick_cli, "start_web_server", _start)

    from click.testing import CliRunner

    r = CliRunner().invoke(pick_cli.pick, ["--web", "--port", "1234", "--no-browser"])
    assert r.exit_code == 0
    assert called["port"] == 1234
    assert called["no_browser"] is True


def test_pick_files_mode_generates_codes_and_calls_server(monkeypatch, tmp_path):
    pick_cli = importlib.import_module("fcbyk.commands.pick.cli")

    f = tmp_path / "a.txt"
    f.write_text("hi", encoding="utf-8")

    monkeypatch.setattr(pick_cli, "load_json_config", lambda *a, **k: {"items": []})

    class _Svc:
        def __init__(self, *a, **k):
            pass

        def generate_redeem_codes(self, n):
            return ["ABCD"]

        def pick_item(self, items):
            raise AssertionError("should not be called")

    monkeypatch.setattr(pick_cli, "PickService", _Svc)

    called = {}

    def _start(port, no_browser, **kwargs):
        called.update({"port": port, "no_browser": no_browser, **kwargs})

    monkeypatch.setattr(pick_cli, "start_web_server", _start)

    from click.testing import CliRunner

    r = CliRunner().invoke(
        pick_cli.pick,
        ["--files", str(f), "--gen-codes", "1", "--show-codes", "--port", "8888"],
    )
    assert r.exit_code == 0
    assert called["files_root"] == str(f)
    assert called["codes"] == ["ABCD"]
    assert called["admin_password"] == "123456"
    assert called["port"] == 8888


def test_pick_files_mode_prompts_password(monkeypatch, tmp_path):
    pick_cli = importlib.import_module("fcbyk.commands.pick.cli")

    f = tmp_path / "a.txt"
    f.write_text("hi", encoding="utf-8")

    monkeypatch.setattr(pick_cli, "load_json_config", lambda *a, **k: {"items": []})

    class _Svc:
        def __init__(self, *a, **k):
            pass

        def generate_redeem_codes(self, n):
            return []

        def pick_item(self, items):
            raise AssertionError("should not be called")

    monkeypatch.setattr(pick_cli, "PickService", _Svc)


    # 用户输入空 => 使用默认 123456
    monkeypatch.setattr("click.prompt", lambda *a, **k: "")

    called = {}

    def _start(port, no_browser, **kwargs):
        called.update(kwargs)

    monkeypatch.setattr(pick_cli, "start_web_server", _start)

    from click.testing import CliRunner

    # 显式指定高端口，避免 CI/Linux 环境下默认 80 需要 root 权限导致提前退出
    r = CliRunner().invoke(pick_cli.pick, ["--files", str(f), "--password", "--port", "8888"])
    assert r.exit_code == 0
    assert called["admin_password"] == "123456"


def test_pick_items_passed_to_service(monkeypatch):
    pick_cli = importlib.import_module("fcbyk.commands.pick.cli")

    monkeypatch.setattr(pick_cli, "load_json_config", lambda *a, **k: {"items": ["x"]})

    picked = {}

    class _Svc:
        def __init__(self, *a, **k):
            pass

        def pick_item(self, items):
            picked["items"] = items

        def generate_redeem_codes(self, *a, **k):
            return []

    monkeypatch.setattr(pick_cli, "PickService", _Svc)

    from click.testing import CliRunner

    r = CliRunner().invoke(pick_cli.pick, ["a", "b"])
    assert r.exit_code == 0
    assert picked["items"] == ["a", "b"]


def test_pick_no_items_available_prints_usage(monkeypatch):
    pick_cli = importlib.import_module("fcbyk.commands.pick.cli")

    monkeypatch.setattr(pick_cli, "load_json_config", lambda *a, **k: {"items": []})

    class _Svc:
        def __init__(self, *a, **k):
            pass

        def pick_item(self, items):
            raise AssertionError("should not be called")

        def generate_redeem_codes(self, *a, **k):
            return []

    monkeypatch.setattr(pick_cli, "PickService", _Svc)

    from click.testing import CliRunner

    r = CliRunner().invoke(pick_cli.pick, [])
    assert r.exit_code == 0
    assert "Error: No items available" in r.output
    assert "Use --add" in r.output

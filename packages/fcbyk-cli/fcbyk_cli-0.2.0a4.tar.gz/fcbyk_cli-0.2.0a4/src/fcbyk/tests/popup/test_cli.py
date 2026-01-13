import importlib


def test_popup_help():
    from click.testing import CliRunner
    from fcbyk.cli import cli

    r = CliRunner().invoke(cli, ["popup", "--help"])
    assert r.exit_code == 0


def test_popup_numbers_less_than_1(monkeypatch):
    popup_cli = importlib.import_module("fcbyk.commands.popup.cli")

    called = {"spawn": 0}

    class _Svc:
        def spawn_many(self, opts):
            called["spawn"] += 1

    monkeypatch.setattr(popup_cli, "PopupService", lambda: _Svc())

    lines = []
    monkeypatch.setattr("click.echo", lambda s="": lines.append(str(s)))

    from click.testing import CliRunner

    r = CliRunner().invoke(popup_cli.popup, ["--numbers", "0"])
    assert r.exit_code == 0
    assert any("greater than 0" in x for x in lines)
    assert called["spawn"] == 0


def test_popup_numbers_too_many_and_user_declines(monkeypatch):
    popup_cli = importlib.import_module("fcbyk.commands.popup.cli")

    called = {"spawn": 0}

    class _Svc:
        def spawn_many(self, opts):
            called["spawn"] += 1

    monkeypatch.setattr(popup_cli, "PopupService", lambda: _Svc())
    monkeypatch.setattr("click.confirm", lambda *_a, **_k: False)

    from click.testing import CliRunner

    r = CliRunner().invoke(popup_cli.popup, ["--numbers", "51"])
    assert r.exit_code == 0
    assert called["spawn"] == 0


def test_popup_numbers_too_many_and_user_accepts(monkeypatch):
    popup_cli = importlib.import_module("fcbyk.commands.popup.cli")

    captured = {}

    class _Svc:
        def spawn_many(self, opts):
            captured["opts"] = opts

    monkeypatch.setattr(popup_cli, "PopupService", lambda: _Svc())
    monkeypatch.setattr("click.confirm", lambda *_a, **_k: True)

    from click.testing import CliRunner

    r = CliRunner().invoke(popup_cli.popup, ["--numbers", "51", "tip1", "tip2"]) 
    assert r.exit_code == 0

    opts = captured["opts"]
    assert opts.numbers == 51
    assert opts.title == "温馨提示"
    assert list(opts.tips) == ["tip1", "tip2"]


def test_popup_normal_calls_service(monkeypatch):
    popup_cli = importlib.import_module("fcbyk.commands.popup.cli")

    captured = {}

    class _Svc:
        def spawn_many(self, opts):
            captured["opts"] = opts

    monkeypatch.setattr(popup_cli, "PopupService", lambda: _Svc())

    from click.testing import CliRunner

    r = CliRunner().invoke(popup_cli.popup, ["--title", "T", "--numbers", "2", "a", "b"]) 
    assert r.exit_code == 0

    opts = captured["opts"]
    assert opts.title == "T"
    assert opts.numbers == 2
    assert list(opts.tips) == ["a", "b"]


import importlib


def test_slide_help():
    from click.testing import CliRunner
    from fcbyk.cli import cli

    runner = CliRunner()
    r = runner.invoke(cli, ["slide", "--help"])
    assert r.exit_code == 0
    assert "PPT remote control" in r.output.lower() or "ppt" in r.output.lower()


def test_slide_cli_uses_localhost_when_no_network(monkeypatch):
    # 只测试：当 get_private_networks 返回空时，会提示 warning，且不会真的启动服务器
    slide_cli = importlib.import_module("fcbyk.commands.slide.cli")

    # prompt 返回密码
    monkeypatch.setattr("click.prompt", lambda *a, **k: "p")

    # 无网卡
    monkeypatch.setattr(slide_cli, "get_private_networks", lambda: [])

    # 避免真实剪贴板
    monkeypatch.setattr(slide_cli.pyperclip, "copy", lambda *_: None)

    # mock create_slide_app 返回 (app, socketio)，且 socketio.run 不做事
    run_kwargs = {}

    class MockSocketIO:
        def run(self, app, **kwargs):
            run_kwargs.update(kwargs)

    mock_socketio = MockSocketIO()
    monkeypatch.setattr(slide_cli, "create_slide_app", lambda service: (object(), mock_socketio))

    # 避免输出 URL 列表逻辑
    monkeypatch.setattr(slide_cli, "echo_network_urls", lambda *a, **k: None)

    from click.testing import CliRunner

    runner = CliRunner()
    r = runner.invoke(slide_cli.slide, ["--port", "1234"])

    assert r.exit_code == 0
    assert "No private network interface found" in r.output
    assert run_kwargs["host"] == "0.0.0.0"
    assert run_kwargs["port"] == 1234


import importlib


def test_lansend_help():
    from click.testing import CliRunner
    from fcbyk.cli import cli

    r = CliRunner().invoke(cli, ["lansend", "--help"])
    assert r.exit_code == 0


def test_lansend_cli_impl_runs_app(monkeypatch, tmp_path):
    """提高 lansend/cli 覆盖率：测试 _lansend_impl 主流程，不启动真实 server/browser/clipboard"""

    lansend_cli = importlib.import_module("fcbyk.commands.lansend.cli")

    # 目录存在
    monkeypatch.setattr(lansend_cli.os.path, "exists", lambda p: True)
    monkeypatch.setattr(lansend_cli.os.path, "isdir", lambda p: True)
    monkeypatch.setattr(lansend_cli.os.path, "abspath", lambda p: str(tmp_path))

    # mock service 与 password
    class _Svc:
        def __init__(self, cfg):
            self.config = cfg

        def pick_upload_password(self, password, un_upload, click_mod):
            return None

    monkeypatch.setattr(lansend_cli, "LansendService", lambda cfg: _Svc(cfg))

    # network/urls
    monkeypatch.setattr(lansend_cli, "get_private_networks", lambda: [{"iface": "Ethernet", "ips": ["192.168.0.2"], "virtual": False, "type": "ethernet", "priority": 10}])
    monkeypatch.setattr(lansend_cli, "echo_network_urls", lambda *a, **k: None)

    # clipboard/browser
    monkeypatch.setattr(lansend_cli.pyperclip, "copy", lambda *_: None)
    monkeypatch.setattr(lansend_cli.webbrowser, "open", lambda *_: None)

    # serve (waitress) - mock waitress 模块的 serve 函数
    ran = {}

    def mock_serve(app, **kw):
        ran.update(kw)

    # Mock waitress 模块（在延迟导入之前，使用 sys.modules）
    import sys
    import types
    mock_waitress = types.ModuleType('waitress')
    mock_waitress.serve = mock_serve
    sys.modules['waitress'] = mock_waitress
    
    monkeypatch.setattr(lansend_cli, "create_lansend_app", lambda service: object())

    lansend_cli._lansend_impl(port=1234, directory=".", password=False, no_browser=True)

    assert ran["host"] == "0.0.0.0"
    assert ran["port"] == 1234

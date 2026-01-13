import importlib


def test_jiahao_help():
    from click.testing import CliRunner
    from fcbyk.cli import cli

    runner = CliRunner()
    result = runner.invoke(cli, ["jiahao", "--help"])
    assert result.exit_code == 0
    assert "Jiahao Hacker Terminal Simulator" in result.output


def test_select_mode_interactively_with_enter_defaults_binary(monkeypatch):
    # 覆盖 select_mode_interactively 的 Enter 分支
    jiahao_cli = importlib.import_module("fcbyk.commands.jiahao.cli")

    monkeypatch.setattr("click.getchar", lambda: "\r")

    mode = jiahao_cli.select_mode_interactively("binary")
    assert mode == jiahao_cli.DisplayMode.BINARY


def test_select_mode_interactively_with_w_key(monkeypatch):
    # 覆盖 w/W 上移逻辑
    jiahao_cli = importlib.import_module("fcbyk.commands.jiahao.cli")

    # 第一次按 w 让 index 往上（从 binary 到 glitch），第二次回车确认
    seq = iter(["w", "\r"])
    monkeypatch.setattr("click.getchar", lambda: next(seq))

    mode = jiahao_cli.select_mode_interactively("binary")
    assert mode == jiahao_cli.DisplayMode.GLITCH


def test_select_mode_interactively_with_s_key(monkeypatch):
    # 覆盖 s/S 下移逻辑
    jiahao_cli = importlib.import_module("fcbyk.commands.jiahao.cli")

    # 第一次按 s 让 index 往下（从 binary 到 code），第二次回车确认
    seq = iter(["s", "\r"])
    monkeypatch.setattr("click.getchar", lambda: next(seq))

    mode = jiahao_cli.select_mode_interactively("binary")
    assert mode == jiahao_cli.DisplayMode.CODE


def test_jiahao_cli_main_flow_calls_terminal(monkeypatch):
    """覆盖 jiahao() 主流程：
    - click.clear
    - enable_windows_ansi
    - select_mode_interactively
    - input 两次
    - time.sleep
    - terminal.run/show_completion_screen
    - finally 恢复光标
    """

    jiahao_cli = importlib.import_module("fcbyk.commands.jiahao.cli")

    monkeypatch.setattr("click.clear", lambda: None)
    monkeypatch.setattr(jiahao_cli, "enable_windows_ansi", lambda: True)
    monkeypatch.setattr(jiahao_cli, "select_mode_interactively", lambda *_: jiahao_cli.DisplayMode.BINARY)

    # 跳过 input 阻塞
    monkeypatch.setattr("builtins.input", lambda *a, **k: "")
    monkeypatch.setattr("time.sleep", lambda *_: None)

    called = {"run": 0, "done": 0, "cursor": []}

    class _Term:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

        def run(self):
            called["run"] += 1

        def show_completion_screen(self):
            called["done"] += 1

    monkeypatch.setattr(jiahao_cli, "HackerTerminal", lambda **kw: _Term(**kw))

    # 捕获 finally 写入
    class _Stdout:
        def __init__(self):
            self.buf = []
            self.closed = False
            self.encoding = 'utf-8'
            self.errors = 'strict'
            self.mode = 'w'

        def write(self, s):
            self.buf.append(s)

        def flush(self):
            pass

        def isatty(self):
            return False

        def close(self):
            self.closed = True

    out = _Stdout()
    monkeypatch.setattr("sys.stdout", out)

    # 直接调用 click command 的回调函数
    jiahao_cli.jiahao.callback(duration=1, speed=0.01, density=0.5)

    assert called["run"] == 1
    assert called["done"] == 1
    # sys.stdout.write 在某些环境可能写入 bytes，这里统一转成 str 再判断
    joined = "".join(x.decode() if isinstance(x, (bytes, bytearray)) else str(x) for x in out.buf)
    assert "\033[?25h" in joined

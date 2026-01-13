import importlib

import pytest

jiahao_service = importlib.import_module("fcbyk.commands.jiahao.service")
TerminalSize = jiahao_service.TerminalSize
TerminalControl = jiahao_service.TerminalControl
HackerTerminal = jiahao_service.HackerTerminal
DisplayMode = jiahao_service.DisplayMode


def test_enable_windows_ansi_import_error_returns_false(monkeypatch):
    # 让 import colorama 触发 ImportError
    import builtins

    real_import = builtins.__import__

    def _import(name, *a, **k):
        if name == "colorama":
            raise ImportError("no")
        return real_import(name, *a, **k)

    monkeypatch.setattr(builtins, "__import__", _import)
    assert jiahao_service.enable_windows_ansi() is False


def test_terminal_control_writes_when_ansi_enabled(monkeypatch):
    buf = []

    class _Stdout:
        def write(self, s):
            buf.append(s)

        def flush(self):
            pass

        def isatty(self):
            return True

    monkeypatch.setattr("sys.stdout", _Stdout())

    tc = TerminalControl(ansi_enabled=True)
    tc.clear_screen()
    tc.hide_cursor()
    tc.show_cursor()
    tc.move_cursor(2, 3)

    joined = "".join(buf)
    assert "\033[2J\033[H" in joined
    assert "\033[?25l" in joined
    assert "\033[?25h" in joined
    assert "\033[3;2H" in joined


def test_render_screen_ansi_branch_writes_and_status(monkeypatch):
    # 覆盖 _render_screen 的 ANSI 分支与 _render_status
    buf = []

    class _Stdout:
        def write(self, s):
            buf.append(s)

        def flush(self):
            pass

        def isatty(self):
            return True

    monkeypatch.setattr("sys.stdout", _Stdout())

    # 固定终端尺寸
    monkeypatch.setattr(TerminalSize, "detect", classmethod(lambda cls: TerminalSize(30, 8)))

    # 固定随机与时间，避免不稳定
    monkeypatch.setattr(jiahao_service.random, "choice", lambda seq: seq[0])
    monkeypatch.setattr(jiahao_service.random, "randint", lambda a, b: a)

    ht = HackerTerminal(mode=DisplayMode.BINARY, duration=5, speed=0.05, density=0.5, ansi_enabled=True)

    # 强制走 ansi 分支
    ht.ansi_enabled = True

    # 用非常短的 lines
    ht._render_screen(["L1", "L2"], elapsed=1.0)

    joined = "".join(buf)
    # move_cursor + 内容行 + status 文本
    assert "L1" in joined
    assert "TARGET:" in joined
    assert "[" in joined  # 进度条


def test_generate_code_screen_inserts_snippet_when_wide(monkeypatch):
    # 让 cols>50 且 rows 足够
    monkeypatch.setattr(TerminalSize, "detect", classmethod(lambda cls: TerminalSize(80, 12)))

    # 控制随机：
    # - random.random 让字符生成与插入逻辑可预测
    monkeypatch.setattr(jiahao_service.random, "random", lambda: 0.0)
    monkeypatch.setattr(jiahao_service.random, "choice", lambda seq: seq[0])

    # randint：用于插入次数、行 r、列 c 等
    # 这里返回 a 保证在合法范围内
    monkeypatch.setattr(jiahao_service.random, "randint", lambda a, b: a)

    ht = HackerTerminal(mode=DisplayMode.CODE, duration=5, speed=0.05, density=0.5, ansi_enabled=False)
    ht.mode = DisplayMode.CODE

    screen = ht._generate_code_screen()
    assert isinstance(screen, list)
    assert len(screen) == ht.size.rows - 2

    # 由于我们让 random.random=0，且 randint=min => 应插入 snippet（带 root@ 或 ACCESS 等）
    assert any("root@" in line or "ACCESS:" in line or "ENCRYPTION:" in line for line in screen)


def test_generate_binary_screen_inserts_hex_block(monkeypatch):
    # 控制尺寸与随机，让 hex block 插入必发生
    monkeypatch.setattr(TerminalSize, "detect", classmethod(lambda cls: TerminalSize(40, 8)))

    # random.random 调用次数较多：
    # - 用队列：先让每个字符生成走 density 分支，再让 hex 插入触发
    seq = [0.0] * 500
    # 在每行结束时的 hex 插入判断 random.random() < 0.05，需要 0.0
    # 已经是 0.0，无需特殊
    it = iter(seq)
    monkeypatch.setattr(jiahao_service.random, "random", lambda: next(it, 0.0))

    monkeypatch.setattr(jiahao_service.random, "choice", lambda s: s[0])
    monkeypatch.setattr(jiahao_service.random, "randint", lambda a, b: a)

    ht = HackerTerminal(mode=DisplayMode.BINARY, duration=5, speed=0.05, density=0.5, ansi_enabled=False)
    screen = ht._generate_binary_screen()

    # hex block 插入会包含 1;33m（黄色）
    assert any("\033[1;33m" in line for line in screen)


def test_show_completion_screen_ansi_branch_writes_prompt(monkeypatch):
    buf = []

    class _Stdout:
        def write(self, s):
            buf.append(s)

        def flush(self):
            pass

        def isatty(self):
            return True

    monkeypatch.setattr("sys.stdout", _Stdout())
    monkeypatch.setattr(TerminalSize, "detect", classmethod(lambda cls: TerminalSize(60, 20)))

    # 固定随机
    monkeypatch.setattr(jiahao_service.random, "randint", lambda a, b: a)
    monkeypatch.setattr(jiahao_service.random, "choice", lambda s: s[0])

    ht = HackerTerminal(mode=DisplayMode.BINARY, duration=3, speed=0.05, density=0.5, ansi_enabled=True)
    ht.ansi_enabled = True

    ht.show_completion_screen()

    joined = "".join(buf)
    assert "Press Enter to return to reality" in joined


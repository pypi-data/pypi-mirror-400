import random

from fcbyk.commands.jiahao.service import (
    DisplayMode,
    HackerTerminal,
    TerminalControl,
    TerminalSize,
)


def test_terminal_size_detect_fallback(monkeypatch):

    import shutil

    def _boom(*a, **k):
        raise RuntimeError("no tty")

    orig = shutil.get_terminal_size
    monkeypatch.setattr(shutil, "get_terminal_size", _boom)

    size = TerminalSize.detect()

    # 立即恢复，避免影响 pytest 后续的终端宽度计算
    monkeypatch.setattr(shutil, "get_terminal_size", orig)
    assert size.columns == 80
    assert size.rows == 24


def test_terminal_control_no_ansi_no_output(monkeypatch):
    # ansi_enabled=False 时，这些方法应直接 return，不写 stdout
    wrote = []

    class _Stdout:
        def write(self, s):
            wrote.append(s)

        def flush(self):
            pass

        def isatty(self):
            return True

    monkeypatch.setattr("sys.stdout", _Stdout())

    tc = TerminalControl(ansi_enabled=False)
    tc.clear_screen()
    tc.hide_cursor()
    tc.show_cursor()
    tc.move_cursor(1, 1)

    assert wrote == []


def test_hacker_terminal_generate_screen_modes(monkeypatch):
    # 固定终端尺寸，避免生成内容过大
    # rows=8 => rows-2=6，可避免 _generate_code_screen 里 randint(2, min(...)) 出现空区间
    monkeypatch.setattr(TerminalSize, "detect", classmethod(lambda cls: TerminalSize(20, 8)))

    ht = HackerTerminal(mode=DisplayMode.BINARY, duration=1, speed=0.1, density=0.5, ansi_enabled=False)

    # binary
    ht.mode = DisplayMode.BINARY
    s1 = ht._generate_screen()
    assert isinstance(s1, list) and len(s1) == ht.size.rows - 2

    # matrix
    ht.mode = DisplayMode.MATRIX
    s2 = ht._generate_screen()
    assert isinstance(s2, list) and len(s2) == ht.size.rows - 2

    # code
    ht.mode = DisplayMode.CODE
    s3 = ht._generate_screen()
    assert isinstance(s3, list) and len(s3) == ht.size.rows - 2

    # glitch
    ht.mode = DisplayMode.GLITCH
    s4 = ht._generate_screen()
    assert isinstance(s4, list) and len(s4) == ht.size.rows - 2


def test_render_screen_when_no_ansi_prints(monkeypatch):
    monkeypatch.setattr(TerminalSize, "detect", classmethod(lambda cls: TerminalSize(10, 5)))

    printed = []
    monkeypatch.setattr("builtins.print", lambda s: printed.append(s))

    ht = HackerTerminal(mode=DisplayMode.BINARY, duration=1, speed=0.1, density=0.5, ansi_enabled=False)
    ht._render_screen(["a", "b", "c"], elapsed=0.1)

    assert printed == ["a\nb\nc"]


def test_run_calls_setup_main_loop_cleanup(monkeypatch):
    monkeypatch.setattr(TerminalSize, "detect", classmethod(lambda cls: TerminalSize(10, 5)))

    ht = HackerTerminal(mode=DisplayMode.BINARY, duration=1, speed=0.1, density=0.5, ansi_enabled=False)

    calls = []

    monkeypatch.setattr(ht, "_setup", lambda: calls.append("setup"))
    monkeypatch.setattr(ht, "_main_loop", lambda: calls.append("loop"))
    monkeypatch.setattr(ht, "_cleanup", lambda: calls.append("cleanup"))

    ht.run()
    assert calls == ["setup", "loop", "cleanup"]


def test_main_loop_stops_when_duration_reached(monkeypatch):
    # 让 time.time() 可控，使循环很快结束
    monkeypatch.setattr(TerminalSize, "detect", classmethod(lambda cls: TerminalSize(10, 5)))

    ht = HackerTerminal(mode=DisplayMode.BINARY, duration=1.0, speed=0.01, density=0.5, ansi_enabled=False)
    ht.running = True
    ht.start_time = 100.0

    # 第一次 time.time 返回 100.0（elapsed=0），第二次返回 101.1（>=duration）
    t = {"n": 0}

    def _time():
        t["n"] += 1
        return 100.0 if t["n"] == 1 else 101.1

    monkeypatch.setattr("time.time", _time)

    # 防止 sleep 真实等待
    monkeypatch.setattr("time.sleep", lambda *_: None)

    # 避免渲染逻辑影响
    monkeypatch.setattr(ht, "_generate_screen", lambda: ["x"])
    monkeypatch.setattr(ht, "_render_screen", lambda *a, **k: None)

    ht._main_loop()
    assert t["n"] >= 2


def test_show_completion_screen_no_ansi_prints(monkeypatch):
    monkeypatch.setattr(TerminalSize, "detect", classmethod(lambda cls: TerminalSize(10, 5)))

    printed = []

    def _print(*args, **kwargs):
        printed.append(" ".join(str(a) for a in args))

    monkeypatch.setattr("builtins.print", _print)

    ht = HackerTerminal(mode=DisplayMode.BINARY, duration=3, speed=0.1, density=0.5, ansi_enabled=False)
    ht.show_completion_screen()

    assert any("OPERATION COMPLETED SUCCESSFULLY" in s for s in printed)
    assert any("Duration:" in s for s in printed)

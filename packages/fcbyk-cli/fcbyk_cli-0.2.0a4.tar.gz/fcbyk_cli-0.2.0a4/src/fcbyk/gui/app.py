"""
GUI 应用程序主模块

负责：
- 整合 UI、单例、进程管理等模块
- 提供外部接口：show_gui, kill_gui, run_gui_standalone
- 作为直接运行时的入口点
"""

import os
import subprocess
import sys
import tempfile
from typing import Optional

from .core.compatibility import HAS_GUI

if HAS_GUI:
    from .core.compatibility import QApplication
    try:
        from PySide6.QtCore import QTimer  # type: ignore
    except Exception:  # pragma: no cover
        try:
            from PyQt5.QtCore import QTimer  # type: ignore
        except Exception:  # pragma: no cover
            QTimer = None  # type: ignore
    from .core import process, singleton
    from .ui.main_window import MainWindow
    from .ui.resources import create_app_icon

_window_instance = None  # type: Optional[MainWindow]
_local_server = None


def run_gui_standalone() -> None:
    """独立运行 GUI（供子进程调用）。

    说明：
    - 该函数会在当前进程内创建 QApplication 并进入事件循环。
    - 使用 Qt 本地套接字实现单例：若已有实例运行，将发送 show 消息并退出。
    """
    if not HAS_GUI:
        print("错误: GUI 依赖未安装。", file=sys.stderr)
        print("请使用以下命令安装 GUI 依赖：", file=sys.stderr)
        print("  pip install fcbyk-cli[gui]", file=sys.stderr)
        print("或", file=sys.stderr)
        print("  pip install PySide6", file=sys.stderr)
        sys.exit(1)

    singleton.ensure_single_instance_or_exit()

    if sys.platform == "win32":
        try:
            import ctypes

            myappid = "fcbyk.cli.gui.v1"
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        except (ImportError, AttributeError):
            pass

    process.write_pid_file()
    process.register_pid_cleanup()

    app = QApplication(sys.argv)
    # 应用级图标用于任务栏等；标题栏图标由 MainWindow 单独设置小尺寸优先。
    app.setWindowIcon(create_app_icon())

    def on_message(message: bytes) -> None:
        global _window_instance
        if message == b"show" and _window_instance:
            if QTimer is not None:
                QTimer.singleShot(0, _window_instance.show_and_raise)
            else:
                _window_instance.show_and_raise()
        elif message == b"kill":
            QApplication.instance().quit()

    global _local_server
    _local_server = singleton.create_server(on_message)

    global _window_instance
    _window_instance = MainWindow()
    _window_instance.show_and_raise()

    sys.exit(app.exec())


def kill_gui(timeout_ms: int = 300, force: bool = True) -> str:
    """关闭 GUI。

    先尝试通过单例 socket 发送 kill（优雅退出），再按需使用 PID 文件强制终止。

    返回：
        - "not_running"  : 没有发现 GUI
        - "requested"    : 已发送 kill 请求（不保证已退出）
        - "terminated"   : 已强制终止
        - "failed"       : 尝试失败
    """
    if not HAS_GUI:
        return "not_running"

    requested = singleton.try_send_message(b"kill", timeout_ms=timeout_ms)

    if requested:
        singleton.sleep_after_request()

    if force and os.path.exists(process.PID_FILE):
        try:
            with open(process.PID_FILE, "r", encoding="utf-8") as f:
                pid_str = f.read().strip()
            pid = int(pid_str) if pid_str else 0
        except Exception:
            pid = 0

        if pid and process.force_terminate(pid):
            process.remove_pid_file()
            return "terminated"

    if requested:
        return "requested"

    return "failed"


def show_gui() -> str:
    """从 CLI 启动/唤醒 GUI（在独立进程中运行）。

    返回值：
        - "activated": 已存在 GUI 实例，已发送唤醒请求
        - "started"  : 新启动了一个 GUI 进程

    说明：
    - CLI 进程会立即返回；GUI 会在独立进程中持续运行。
    - 仅负责启动，不在此处创建 QApplication。
    """
    if not HAS_GUI:
        raise ImportError(
            "GUI 依赖未安装。请使用以下命令安装：\n"
            "  pip install fcbyk-cli[gui]\n"
            "或\n"
            "  pip install PySide6"
        )

    if singleton.try_send_message(b"show", timeout_ms=80):
        return "activated"

    python_exe = sys.executable
    # 注意：不能直接运行 app.py 文件（相对导入会失败），应以模块方式启动。
    # 用 `-m fcbyk.gui` 走包入口（__main__.py），避免 runpy 重复加载警告。
    cmd = [python_exe, "-m", "fcbyk.gui"]

    # 将子进程 stdout/stderr 写入日志，避免“启动没反应”时无法排查
    log_file = os.path.join(tempfile.gettempdir(), "fcbyk_gui.log")
    try:
        log_fp = open(log_file, "a", encoding="utf-8")
    except Exception:
        log_fp = None

    try:
        if sys.platform == "win32":
            # Python 3.6 的 subprocess 可能没有 DETACHED_PROCESS 常量；这里做兼容处理。
            creationflags = getattr(subprocess, "DETACHED_PROCESS", 0)
            subprocess.Popen(
                cmd,
                creationflags=creationflags,
                stdin=subprocess.DEVNULL,
                stdout=log_fp or subprocess.DEVNULL,
                stderr=log_fp or subprocess.DEVNULL,
                close_fds=False,
            )
        else:
            subprocess.Popen(
                cmd,
                stdin=subprocess.DEVNULL,
                stdout=log_fp or subprocess.DEVNULL,
                stderr=log_fp or subprocess.DEVNULL,
                start_new_session=True,
                close_fds=True,
            )
    except Exception as e:
        if log_fp:
            try:
                log_fp.flush()
            except Exception:
                pass
        raise RuntimeError(f"无法启动独立 GUI 进程: {e}") from e

    return "started"


if __name__ == "__main__":
    run_gui_standalone()

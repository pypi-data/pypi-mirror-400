"""进程相关工具：PID 文件、进程存在性检测。"""

import atexit
import os
import signal
import subprocess
import sys

from ...utils.config import get_config_path
import time

# PID 文件放在配置目录：~/.fcbyk/fcbyk_gui.pid（Windows 下同样会展开到用户目录）
PID_FILE = get_config_path("fcbyk", "fcbyk_gui.pid")


def write_pid_file() -> None:
    """写入 PID 文件。

    额外逻辑：如果发现旧 PID 文件存在，但对应进程已不存在，则先删除旧 PID 文件，
    避免异常退出导致的 PID 残留影响后续管理。
    """
    try:
        os.makedirs(os.path.dirname(PID_FILE), exist_ok=True)

        # 清理残留 PID（例如崩溃/断电/强杀导致 atexit 未执行）
        if os.path.exists(PID_FILE):
            try:
                with open(PID_FILE, "r", encoding="utf-8") as f:
                    old_pid_str = f.read().strip()
                old_pid = int(old_pid_str) if old_pid_str else 0
            except Exception:
                old_pid = 0

            if old_pid and (not process_exists(old_pid)):
                try:
                    os.remove(PID_FILE)
                except Exception:
                    pass

        with open(PID_FILE, "w", encoding="utf-8") as f:
            f.write(str(os.getpid()))
    except Exception:
        pass


def remove_pid_file() -> None:
    try:
        if os.path.exists(PID_FILE):
            os.remove(PID_FILE)
    except Exception:
        pass


def register_pid_cleanup() -> None:
    atexit.register(remove_pid_file)


def process_exists(pid: int) -> bool:
    """跨平台粗略判断进程是否存在"""
    if pid <= 0:
        return False

    if sys.platform == "win32":
        try:
            out = subprocess.check_output(
                ["tasklist", "/FI", f"PID eq {pid}"],
                stderr=subprocess.DEVNULL,
                stdin=subprocess.DEVNULL,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            ).decode(errors="ignore")
            return str(pid) in out
        except Exception:
            return False

    try:
        os.kill(pid, 0)
        return True
    except Exception:
        return False


def force_terminate(pid: int) -> bool:
    """尽力强杀指定 PID。返回是否确认已不存在。"""
    if not pid or not process_exists(pid):
        return True

    try:
        if sys.platform == "win32":
            subprocess.Popen(
                ["taskkill", "/PID", str(pid), "/T", "/F"],
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            ).wait(timeout=3)
        else:
            os.kill(pid, signal.SIGTERM)
        time.sleep(0.2)
    except Exception:
        pass

    return not process_exists(pid)


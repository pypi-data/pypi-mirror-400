"""进程相关工具：PID 文件、进程存在性检测。"""

import atexit
import os
import signal
import subprocess
import sys
import tempfile
import time

PID_FILE = os.path.join(tempfile.gettempdir(), "fcbyk_gui.pid")


def write_pid_file() -> None:
    try:
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


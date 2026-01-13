"""单例/IPC：通过 Qt 本地套接字实现 GUI 单例与消息通信。"""

import sys
import time
from typing import Callable, Optional

from .compatibility import QLocalServer, QLocalSocket

# Qt 本地套接字在 Windows 上对名字有要求（不能包含 '-' 等），否则会报 Invalid name。
SINGLETON_SERVER_NAME = "fcbyk_gui_singleton"
LEGACY_SINGLETON_SERVER_NAME = "fcbyk-gui-singleton"


def try_send_message(message: bytes, timeout_ms: int = 100) -> bool:
    """尝试向已存在实例发送消息。成功返回 True。"""
    for name in (SINGLETON_SERVER_NAME, LEGACY_SINGLETON_SERVER_NAME):
        try:
            s = QLocalSocket()
            s.connectToServer(name)
            if s.waitForConnected(timeout_ms):
                s.write(message)
                s.flush()
                try:
                    s.waitForBytesWritten(timeout_ms)
                except Exception:
                    pass
                s.disconnectFromServer()
                s.close()
                return True
        except Exception:
            continue
    return False


def ensure_single_instance_or_exit() -> None:
    """若已有实例则发送 show 并退出当前进程。"""
    if try_send_message(b"show", timeout_ms=100):
        raise SystemExit(0)


def create_server(on_message: Callable[[bytes], None]) -> Optional[QLocalServer]:
    """创建并监听单例服务。成功返回 QLocalServer，否则返回 None。"""
    try:
        if sys.platform == "win32":
            QLocalServer.removeServer(SINGLETON_SERVER_NAME)
            QLocalServer.removeServer(LEGACY_SINGLETON_SERVER_NAME)

        server = QLocalServer()

        def handle_new_connection():
            socket = server.nextPendingConnection()
            if not socket:
                return
            socket.waitForReadyRead(100)
            data = socket.readAll()
            if isinstance(data, bytes):
                data_bytes = data
            else:
                data_bytes = data.data() if hasattr(data, "data") else bytes(data)
            try:
                on_message(data_bytes)
            finally:
                socket.disconnectFromServer()
                socket.close()

        if server.listen(SINGLETON_SERVER_NAME):
            server.newConnection.connect(handle_new_connection)
            return server

    except Exception:
        return None

    return None


def sleep_after_request():
    """给 GUI 一点时间处理请求并退出（用于 kill 之后）。"""
    time.sleep(0.2)


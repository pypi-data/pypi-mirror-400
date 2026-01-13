"""端口工具函数

提供跨命令复用的端口占用检测。
"""

import socket


def ensure_port_available(port: int, host: str = "0.0.0.0") -> None:
    """确保端口可用，否则抛出 OSError。

    说明：
    - 不启用 SO_REUSEADDR，避免在部分平台/场景下出现“端口已被占用但 bind 仍成功”的误判。
    - 调用方可以捕获 OSError 并输出友好提示。
    """

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, int(port)))


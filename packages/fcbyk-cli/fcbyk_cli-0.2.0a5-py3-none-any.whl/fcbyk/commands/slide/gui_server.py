"""Slide：GUI 子进程入口。

GUI 通过子进程启动 slide Web 服务（Flask + Socket.IO），从而实现：
- 启动/停止 slide 服务不影响主 GUI 进程

启动方式（由 GUI 调用）：
    python -m fcbyk.commands.slide.gui_server --port <port> --password <password>

停止方式：
- 由 GUI 对子进程执行 terminate/kill（更可靠，避免依赖 werkzeug shutdown 钩子）。
"""

import argparse

from .controller import create_slide_app
from .service import SlideService


def main(argv=None):
    # type: (list) -> int
    parser = argparse.ArgumentParser(prog="fcbyk-slide-gui-server")
    parser.add_argument("--port", type=int, required=True)
    parser.add_argument("--password", type=str, required=True)
    args = parser.parse_args(argv)

    service = SlideService(args.password)
    app, socketio = create_slide_app(service)

    socketio.run(
        app,
        host="0.0.0.0",
        port=args.port,
        allow_unsafe_werkzeug=True,
    )

    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())

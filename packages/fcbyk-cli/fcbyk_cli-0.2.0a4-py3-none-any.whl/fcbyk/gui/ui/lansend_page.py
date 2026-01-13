"""LANSend 页面（从 MainWindow 拆分）。

该模块负责：
- LANSend UI 的构建
- LANSend 后台子进程的启动/停止
- 运行状态渲染与日志输出

注意：为保持当前实现最小改动，子进程启动仍使用 `python -c` 导入
`_run_lansend_server_process`。因此该函数也放在本模块中，供子进程导入。
"""

import os
import subprocess
import sys
import tempfile
import webbrowser
from typing import Optional

from ..core.compatibility import (
    QCheckBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from fcbyk.commands.lansend.controller import create_lansend_app
from fcbyk.commands.lansend.service import LansendConfig, LansendService
from fcbyk.utils.network import get_private_networks
from fcbyk.utils.port import ensure_port_available


def _run_lansend_server_process(
    port: int,
    shared_directory: str,
    upload_password: Optional[str],
    un_download: bool,
    un_upload: bool,
    chat_enabled: bool,
) -> None:
    """在独立的子进程中运行 Lansend 服务器。"""

    config = LansendConfig(
        shared_directory=shared_directory,
        upload_password=upload_password,
        un_download=un_download,
        un_upload=un_upload,
        chat_enabled=chat_enabled,
    )
    service = LansendService(config)
    app = create_lansend_app(service)

    from waitress import serve

    serve(app, host="0.0.0.0", port=port)


class LansendPage(QWidget):
    """LANSend 功能页。

    设计目标：
    - 主窗口只负责承载/导航；页面负责自己的 UI + 业务逻辑
    - 后续新增其它命令页面时，可按相同模式扩展
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        # server 状态
        self._server_proc = None  # type: Optional[subprocess.Popen]
        self._server_running = False
        self._server_error = None  # type: Optional[str]

        # 日志文件放到 ~/.fcbyk/ 目录下（与 CLI 配置目录统一）
        try:
            from fcbyk.utils.config import get_config_path

            self._server_log_file = get_config_path("fcbyk", "fcbyk_lansend.log")
            os.makedirs(os.path.dirname(self._server_log_file), exist_ok=True)
        except Exception:
            # 回退到系统临时目录
            self._server_log_file = os.path.join(tempfile.gettempdir(), "fcbyk_lansend.log")

        layout = QVBoxLayout()
        self.setLayout(layout)

        self._build_ui(layout)

    # -----------------
    # UI
    # -----------------

    def _build_ui(self, root_layout: QVBoxLayout) -> None:
        title = QLabel("LANSend（局域网文件共享）")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        root_layout.addWidget(title)

        # 目录选择
        row_dir = QHBoxLayout()
        root_layout.addLayout(row_dir)

        row_dir.addWidget(QLabel("共享目录:"))
        self._dir_input = QLineEdit()
        self._dir_input.setText(os.getcwd())
        row_dir.addWidget(self._dir_input, 1)

        btn_browse = QPushButton("选择...")
        btn_browse.clicked.connect(self._on_browse_directory)
        row_dir.addWidget(btn_browse)

        # 端口
        row_port = QHBoxLayout()
        root_layout.addLayout(row_port)

        row_port.addWidget(QLabel("端口:"))
        self._port_input = QLineEdit()
        self._port_input.setText("80")
        self._port_input.setFixedWidth(120)
        row_port.addWidget(self._port_input)
        row_port.addStretch(1)

        # 选项
        row_opts = QHBoxLayout()
        root_layout.addLayout(row_opts)

        self._chk_password = QCheckBox("启用上传密码（默认 123456，可在启动时输入）")
        self._chk_no_browser = QCheckBox("不自动打开浏览器")
        self._chk_un_download = QCheckBox("隐藏下载按钮")
        self._chk_un_upload = QCheckBox("禁用上传")
        self._chk_chat = QCheckBox("启用聊天")

        # 适配小窗口：分两列
        opts_left = QVBoxLayout()
        opts_right = QVBoxLayout()
        opts_left.addWidget(self._chk_password)
        opts_left.addWidget(self._chk_no_browser)
        opts_left.addWidget(self._chk_chat)
        opts_right.addWidget(self._chk_un_download)
        opts_right.addWidget(self._chk_un_upload)
        opts_right.addStretch(1)
        row_opts.addLayout(opts_left, 1)
        row_opts.addLayout(opts_right, 1)

        # 按钮区
        row_btns = QHBoxLayout()
        root_layout.addLayout(row_btns)

        self._btn_start = QPushButton("启动共享")
        self._btn_start.clicked.connect(self._on_toggle_server)
        row_btns.addWidget(self._btn_start)

        self._btn_open = QPushButton("打开页面")
        self._btn_open.clicked.connect(self._on_open_in_browser)
        self._btn_open.setEnabled(False)
        row_btns.addWidget(self._btn_open)

        self._btn_open_log = QPushButton("打开日志")
        self._btn_open_log.clicked.connect(self._on_open_log_file)
        row_btns.addWidget(self._btn_open_log)

        row_btns.addStretch(1)

        # 状态/日志
        self._status_label = QLabel("状态：未启动")
        root_layout.addWidget(self._status_label)

        self._log = QTextEdit()
        self._log.setReadOnly(True)
        self._log.setPlaceholderText("这里会显示启动信息、访问地址、错误等")
        root_layout.addWidget(self._log, 1)

        # 初始状态渲染
        self._last_url = None  # type: Optional[str]
        self._refresh_status_ui()

    # -----------------
    # helpers
    # -----------------

    def stop_if_running(self) -> None:
        """供 MainWindow 退出时调用：如果正在运行就停止。"""
        try:
            if self._server_running:
                self._stop_server()
        except Exception:
            pass

    def _append_log(self, text: str) -> None:
        self._log.append(text)

    def _set_start_button_running(self, running: bool) -> None:
        if running:
            self._btn_start.setText("停止共享")
            self._btn_start.setStyleSheet("background-color: #d9534f; color: white; font-weight: bold;")
        else:
            self._btn_start.setText("启动共享")
            self._btn_start.setStyleSheet("")

    def _refresh_status_ui(self) -> None:
        running = bool(self._server_running)
        if running:
            self._set_start_button_running(True)
            self._btn_open.setEnabled(bool(self._last_url))
            self._status_label.setText(f"状态：运行中 {self._last_url or ''}")
        else:
            self._set_start_button_running(False)
            self._btn_open.setEnabled(False)
            if self._server_error:
                self._status_label.setText(f"状态：启动失败 - {self._server_error}")
            else:
                self._status_label.setText("状态：未启动")

    def _on_browse_directory(self) -> None:
        d = QFileDialog.getExistingDirectory(self, "选择共享目录", self._dir_input.text() or os.getcwd())
        if d:
            self._dir_input.setText(d)

    def _parse_port(self):  # type: () -> Optional[int]
        raw = (self._port_input.text() or "").strip()
        if not raw:
            return None
        try:
            port = int(raw)
        except ValueError:
            return None
        if port <= 0 or port > 65535:
            return None
        return port

    @staticmethod
    def _is_port_available(port: int, host: str = "0.0.0.0") -> bool:
        """检测端口是否可用。"""

        try:
            ensure_port_available(port=port, host=host)
            return True
        except OSError:
            return False

    def _build_local_url(self, port: int) -> str:
        private_networks = get_private_networks()
        if private_networks:
            local_ip = private_networks[0]["ips"][0]
        else:
            local_ip = "127.0.0.1"
        return f"http://{local_ip}:{port}"

    def _on_open_in_browser(self) -> None:
        if self._last_url:
            webbrowser.open(self._last_url)

    def _on_open_log_file(self) -> None:
        path = getattr(self, "_server_log_file", None)
        if not path:
            QMessageBox.information(self, "日志", "未配置日志文件路径。")
            return

        # 确保文件存在（即使为空）
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            if not os.path.exists(path):
                with open(path, "a", encoding="utf-8"):
                    pass
        except Exception as e:
            QMessageBox.warning(self, "打开失败", f"无法创建/访问日志文件：{e}\n\n路径：{path}")
            return

        try:
            if sys.platform == "win32":
                # Windows: 用记事本打开
                subprocess.Popen(["notepad.exe", path], close_fds=True)
            else:
                # macOS/Linux: 使用默认应用打开
                if sys.platform == "darwin":
                    subprocess.Popen(["open", path], close_fds=True)
                else:
                    subprocess.Popen(["xdg-open", path], close_fds=True)
        except Exception as e:
            QMessageBox.warning(self, "打开失败", f"无法打开日志文件：{e}\n\n路径：{path}")

    # -----------------
    # server control
    # -----------------

    def _on_toggle_server(self) -> None:
        if self._server_running:
            self._stop_server()
        else:
            self._start_server()

    def _stop_server(self) -> None:
        if not self._server_proc or self._server_proc.poll() is not None:
            self._server_running = False
            self._server_proc = None
            self._append_log("服务器未在运行。")
            self._refresh_status_ui()
            return

        try:
            if sys.platform == "win32":
                # Windows 下强制终止进程树
                import ctypes

                PROCESS_TERMINATE = 1
                PROCESS_QUERY_INFORMATION = 0x0400
                handle = ctypes.windll.kernel32.OpenProcess(
                    PROCESS_TERMINATE | PROCESS_QUERY_INFORMATION, False, self._server_proc.pid
                )
                ctypes.windll.kernel32.TerminateProcess(handle, 1)
                ctypes.windll.kernel32.CloseHandle(handle)
            else:
                self._server_proc.terminate()

            self._server_proc.wait(timeout=2)
            self._append_log("服务器已停止。")
        except Exception as e:
            self._append_log(f"停止服务器时出错: {e}")
        finally:
            self._server_running = False
            self._server_proc = None
            self._refresh_status_ui()

    def _start_server(self) -> None:
        directory = (self._dir_input.text() or "").strip()
        if not directory:
            QMessageBox.warning(self, "参数错误", "请选择共享目录")
            return

        if not os.path.exists(directory):
            QMessageBox.warning(self, "参数错误", f"目录不存在：{directory}")
            return

        if not os.path.isdir(directory):
            QMessageBox.warning(self, "参数错误", f"不是目录：{directory}")
            return

        port = self._parse_port()
        if port is None:
            QMessageBox.warning(self, "参数错误", "端口无效，请输入 1~65535 的整数")
            return

        # 端口占用检测：尽量在启动前提示
        if not self._is_port_available(port):
            QMessageBox.warning(self, "端口被占用", f"端口 {port} 已被占用，请更换端口后重试。")
            return

        shared_directory = os.path.abspath(directory)

        password_flag = bool(self._chk_password.isChecked())
        no_browser = bool(self._chk_no_browser.isChecked())
        un_download = bool(self._chk_un_download.isChecked())
        un_upload = bool(self._chk_un_upload.isChecked())
        chat = bool(self._chk_chat.isChecked())

        # 组装配置（service/app 在子进程中创建）
        upload_password = None  # type: Optional[str]

        # GUI 模式下，不引入 click 交互：
        # - 如果勾选“启用上传密码”且未禁用上传，则弹窗输入（可空 -> 默认 123456）
        if password_flag and (not un_upload):
            pw_val = self._prompt_password(default_value="123456")
            if pw_val is None:
                return
            upload_password = pw_val

        url = self._build_local_url(port)
        self._last_url = url

        self._append_log(f"目录: {shared_directory}")
        self._append_log(f"端口: {port}")
        self._append_log(f"URL: {url}")
        self._append_log(f"隐藏下载: {un_download}  禁用上传: {un_upload}  聊天: {chat}")
        self._append_log(f"上传密码: {'启用' if bool(upload_password) else '未启用'}")

        if not no_browser:
            webbrowser.open(url)

        self._server_error = None

        # 用 subprocess 启动“无控制台窗口”的 python 子进程（Windows 下避免弹黑框）。
        # 注意：用 -c 运行顶层函数，避免 multiprocessing 的 spawn 控制台问题。
        code = (
            "from fcbyk.gui.ui.lansend_page import _run_lansend_server_process; "
            f"_run_lansend_server_process({port!r}, {shared_directory!r}, {upload_password!r}, {un_download!r}, {un_upload!r}, {chat!r})"
        )

        try:
            log_fp = open(self._server_log_file, "a", encoding="utf-8")
        except Exception:
            log_fp = subprocess.DEVNULL

        try:
            creationflags = 0
            if sys.platform == "win32":
                creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0)

            proc = subprocess.Popen(
                [sys.executable, "-c", code],
                stdin=subprocess.DEVNULL,
                stdout=log_fp,
                stderr=log_fp,
                creationflags=creationflags,
                close_fds=(sys.platform != "win32"),
            )
        except Exception as e:
            self._server_error = str(e)
            self._server_running = False
            self._refresh_status_ui()
            QMessageBox.critical(self, "启动失败", f"启动服务器失败：{e}\n\n日志: {self._server_log_file}")
            return

        self._server_proc = proc
        self._server_running = True
        self._append_log("服务器已启动（在后台进程中运行）。")
        self._append_log(f"日志文件: {self._server_log_file}")

        self._refresh_status_ui()

    def _prompt_password(self, default_value: str = "123456") -> Optional[str]:
        """弹窗提示用户输入上传密码。

        返回：
        - str : 用户输入（为空则返回 default_value）
        - None: 用户取消
        """

        box = QMessageBox(self)
        box.setWindowTitle("上传密码")
        box.setText(f"请输入上传密码（留空则使用默认：{default_value}）")
        box.setIcon(QMessageBox.Icon.Question)

        inp = QLineEdit(box)
        inp.setEchoMode(QLineEdit.EchoMode.Password)
        inp.setPlaceholderText(default_value)

        # 尽量把输入框撑开一点
        try:
            inp.setMinimumWidth(260)
            inp.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        except Exception:
            pass

        # QMessageBox 的 layout 为 grid，直接 addWidget 即可插入到最后一行
        try:
            box.layout().addWidget(inp)
        except Exception:
            pass

        box.setStandardButtons(QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
        ret = box.exec()
        if ret != QMessageBox.StandardButton.Ok:
            return None

        return (inp.text() or "").strip() or default_value


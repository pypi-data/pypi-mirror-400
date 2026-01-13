"""Slide 页面：PPT 远程控制。

功能：
- 启动/停止 Slide 服务（通过子进程）
- 显示访问 URL，支持一键复制
- 子进程方案：避免影响 GUI 主进程
"""

import subprocess
import sys
from dataclasses import dataclass

import pyperclip

from ..core.compatibility import (
    QCheckBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
    Qt,
)

from ...utils.network import get_private_networks
from ...utils.port import ensure_port_available


@dataclass
class _ServerInfo:
    """Slide 服务状态。"""
    running: bool = False
    ip: str = ""
    port: int = 0
    password: str = ""


class SlidePage(QWidget):
    """PPT 远程控制页面。"""

    def _on_toggle_clicked(self):
        """合并后的启动/停止按钮点击。"""
        if self._server.running:
            self._on_stop_clicked()
        else:
            self._on_start_clicked()

    def _sync_toggle_button(self):
        """根据运行状态同步按钮文案/样式。"""
        if getattr(self, "_btn_toggle", None) is None:
            return

        if self._server.running:
            self._btn_toggle.setText("停止")
            # 启动后显示红色停止按钮
            self._btn_toggle.setEnabled(True)
            self._btn_toggle.setStyleSheet(
                "QPushButton { padding: 6px 14px; font-weight: 600; "
                "background-color: #e53935; color: white; border: 1px solid #c62828; border-radius: 4px; }"
                "QPushButton:hover { background-color: #d32f2f; }"
                "QPushButton:pressed { background-color: #c62828; }"
                "QPushButton:disabled { background-color: #ef9a9a; color: #fff; border-color: #ef9a9a; }"
            )
        else:
            self._btn_toggle.setText("启动")
            self._btn_toggle.setEnabled(True)
            self._btn_toggle.setStyleSheet(
                "QPushButton { padding: 6px 14px; font-weight: 600; }"
            )

    def __init__(self, parent=None):
        super().__init__(parent)
        self._server = _ServerInfo()
        self._proc = None  # type: subprocess.Popen
        self._build_ui()
        self._sync_toggle_button()

    def _build_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        # 标题
        title = QLabel("PPT 远程控制（Slide）")
        title.setStyleSheet("font-size: 16px; font-weight: 600;")
        layout.addWidget(title)

        # 状态
        self._status = QLabel("状态：未启动")
        layout.addWidget(self._status)

        # 表单
        form = QVBoxLayout()

        # 端口输入
        port_row = QHBoxLayout()
        port_row.addWidget(QLabel("端口："))
        self._port = QLineEdit("80")
        self._port.setPlaceholderText("例如 80 / 8080")
        self._port.setMaximumWidth(120)
        port_row.addWidget(self._port)
        port_row.addStretch(1)
        form.addLayout(port_row)

        # 密码输入
        pwd_row = QHBoxLayout()
        pwd_row.addWidget(QLabel("密码："))
        self._password = QLineEdit()
        self._password.setEchoMode(QLineEdit.EchoMode.Password)
        self._password.setPlaceholderText("设置访问密码")
        self._password.setMaximumWidth(240)
        pwd_row.addWidget(self._password)

        self._show_password = QCheckBox("显示")
        self._show_password.toggled.connect(self._on_toggle_show_password)
        pwd_row.addWidget(self._show_password)
        pwd_row.addStretch(1)
        form.addLayout(pwd_row)

        layout.addLayout(form)

        # 按钮
        btn_layout = QHBoxLayout()

        # 启动/停止 合并为一个按钮
        self._btn_toggle = QPushButton("启动")
        self._btn_toggle.setStyleSheet(
            "QPushButton { padding: 6px 14px; font-weight: 600; }"
        )
        self._btn_toggle.clicked.connect(self._on_toggle_clicked)
        btn_layout.addWidget(self._btn_toggle)

        self._btn_copy = QPushButton("复制链接")
        self._btn_copy.setEnabled(False)
        self._btn_copy.clicked.connect(self._on_copy_clicked)
        btn_layout.addWidget(self._btn_copy)
        btn_layout.addStretch(1)

        layout.addLayout(btn_layout)

        # URL 显示
        self._url = QLabel("")
        self._url.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self._url.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        layout.addWidget(self._url)

        # 帮助文本
        help_text = QLabel(
            "使用方法：\n"
            "1) 设置端口与密码，点击【启动】\n"
            "2) 手机/电脑浏览器打开 URL，输入密码\n"
            "3) 在网页端控制 PPT 翻页与鼠标\n\n"
            "说明：Slide 服务运行在独立子进程中，停止后端口立即释放。"
        )
        help_text.setWordWrap(True)
        layout.addWidget(help_text)

        layout.addStretch(1)

    def _on_toggle_show_password(self, checked: bool):
        """切换密码可见性。"""
        self._password.setEchoMode(
            QLineEdit.EchoMode.Normal if checked else QLineEdit.EchoMode.Password
        )

    def _resolve_local_ip(self) -> str:
        """获取本地 IP 地址（用于生成访问 URL）。"""
        networks = get_private_networks()
        return networks[0]["ips"][0] if networks and networks[0].get("ips") else "127.0.0.1"

    def _on_start_clicked(self):
        """启动 Slide 服务。"""
        if self._server.running:
            return

        # 解析端口
        try:
            port = int(self._port.text().strip())
            if not (0 < port <= 65535):
                raise ValueError("端口范围 1-65535")
        except ValueError as e:
            QMessageBox.warning(self, "参数错误", f"无效的端口：{e}")
            return

        password = self._password.text().strip()
        if not password:
            QMessageBox.warning(self, "参数错误", "密码不能为空")
            return

        # 检查端口占用
        try:
            ensure_port_available(port, host="0.0.0.0")
        except OSError as e:
            QMessageBox.critical(self, "端口不可用", f"端口 {port} 已被占用或无权限使用。\n\n{e}")
            return

        # 启动子进程
        local_ip = self._resolve_local_ip()
        url = f"http://{local_ip}:{port}"

        try:
            self._proc = subprocess.Popen(
                [
                    sys.executable,
                    "-m",
                    "fcbyk.commands.slide.gui_server",
                    "--port",
                    str(port),
                    "--password",
                    password,
                ],
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0) if sys.platform == "win32" else 0,
            )
        except Exception as e:
            QMessageBox.critical(self, "启动失败", f"无法启动 Slide 服务：{e}")
            return

        self._server = _ServerInfo(running=True, ip=local_ip, port=port, password=password)
        self._status.setText(f"状态：运行中（PID: {self._proc.pid}）")
        self._url.setText(url)

        # 更新 UI 状态
        self._sync_toggle_button()
        self._btn_copy.setEnabled(True)
        self._port.setEnabled(False)
        self._password.setEnabled(False)
        self._show_password.setEnabled(False)

        # 复制 URL 到剪贴板
        try:
            pyperclip.copy(url)
            QMessageBox.information(
                self,
                "已启动",
                f"Slide 服务已启动：\n{url}\n\n（URL 已复制到剪贴板）",
            )
        except Exception as e:
            QMessageBox.information(
                self,
                "已启动",
                f"Slide 服务已启动：\n{url}\n\n（无法复制到剪贴板：{e}）",
            )

    def _on_stop_clicked(self):
        """停止 Slide 服务。"""
        if not self._server.running or self._proc is None:
            return

        try:
            # 先尝试优雅停止
            self._proc.terminate()
            try:
                self._proc.wait(timeout=2)
            except subprocess.TimeoutExpired:
                # 超时后强制终止
                self._proc.kill()
                self._proc.wait(timeout=2)
        except Exception as e:
            QMessageBox.warning(self, "停止失败", f"停止 Slide 服务时出错：{e}")
            return
        finally:
            self._proc = None

        self._server.running = False
        self._status.setText("状态：已停止")
        self._url.setText("")

        # 恢复 UI 状态
        self._sync_toggle_button()
        self._btn_copy.setEnabled(False)
        self._port.setEnabled(True)
        self._password.setEnabled(True)
        self._show_password.setEnabled(True)

    def _on_copy_clicked(self):
        """复制访问 URL 到剪贴板。"""
        if not self._server.running:
            return

        url = f"http://{self._server.ip}:{self._server.port}"
        try:
            pyperclip.copy(url)
            QMessageBox.information(self, "已复制", f"已复制：{url}")
        except Exception as e:
            QMessageBox.warning(self, "复制失败", f"无法复制到剪贴板：{e}\n\n{url}")

    def stop_if_running(self):
        """供主窗口退出前调用：确保停止 Slide 服务。"""
        if self._server.running:
            self._on_stop_clicked()
"""Pick 抽奖功能页面。

功能：
- 两种抽奖模式：普通模式（列表抽奖）和文件抽奖模式
- 启动/停止抽奖服务器
- 管理抽奖元素（通过子窗口）
- 支持兑换码生成（文件模式）
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
    QRadioButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from fcbyk.commands.pick.controller import start_web_server
from fcbyk.commands.pick.service import PickService


def _run_pick_server_process(
    port: int,
    no_browser: bool,
    files_root: Optional[str],
    gen_codes: int,
    show_codes: bool,
    codes_dump_file: Optional[str],
    admin_password: str,
) -> None:
    """在独立子进程中运行 Pick 服务器（复用 controller.start_web_server）。

    说明：
    - 普通模式：files_root=None
    - 文件模式：files_root=路径（文件或目录）
    - 兑换码：gen_codes>0 则生成
    """

    codes = None
    if files_root and gen_codes and gen_codes > 0:
        service = PickService(config_file="", default_config={"items": []})
        codes = list(service.generate_redeem_codes(gen_codes))

        # 将本次生成的兑换码写入文件，供 GUI 弹窗展示
        if codes_dump_file:
            try:
                with open(codes_dump_file, "w", encoding="utf-8") as f:
                    f.write("\n".join(codes))
            except Exception:
                pass

        if show_codes:
            print("\nGenerated redeem codes (each can be used once):")
            for c in codes:
                print(f"  {c}")

    start_web_server(
        port=port,
        no_browser=no_browser,
        files_root=files_root,
        codes=codes,
        admin_password=admin_password,
    )

from fcbyk.utils.config import get_config_path, load_json_config
from fcbyk.utils.port import ensure_port_available
from .pick_items_dialog import PickItemsManagerDialog
from .pick_codes_dialog import PickCodesDialog


class PickPage(QWidget):
    """抽奖功能页面"""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._server_proc = None
        self._server_running = False
        self._server_error = None
        self._server_log_file = os.path.join(tempfile.gettempdir(), "fcbyk_pick.log")
        self._codes_dump_file = os.path.join(tempfile.gettempdir(), "fcbyk_pick_codes.txt")
        self._build_ui()

    def _set_files_rows_visible(self, visible: bool) -> None:
        """显示/隐藏文件模式相关行。"""

        try:
            for i in range(self._file_row.count()):
                w = self._file_row.itemAt(i).widget()
                if w is not None:
                    w.setVisible(visible)
        except Exception:
            pass

        try:
            for i in range(self._code_row.count()):
                w = self._code_row.itemAt(i).widget()
                if w is not None:
                    w.setVisible(visible)
        except Exception:
            pass

    def _build_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        # 标题
        title = QLabel("抽奖功能")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)

        # 所有设置放在一起（不分多个 GroupBox）

        # 第一行：模式 + 管理按钮 + items 计数
        row_mode = QHBoxLayout()
        layout.addLayout(row_mode)

        row_mode.addWidget(QLabel("模式："))
        self._mode_normal = QRadioButton("普通")
        self._mode_files = QRadioButton("文件")
        self._mode_normal.setChecked(True)
        self._mode_normal.toggled.connect(self._on_mode_changed)
        self._mode_files.toggled.connect(self._on_mode_changed)
        row_mode.addWidget(self._mode_normal)
        row_mode.addWidget(self._mode_files)

        row_mode.addStretch(1)

        btn_manage = QPushButton("管理")
        btn_manage.clicked.connect(self._on_manage_items)
        row_mode.addWidget(btn_manage)

        self._items_count = QLabel("0")
        self._items_count.setToolTip("当前抽奖元素数量")
        row_mode.addWidget(QLabel("items:"))
        row_mode.addWidget(self._items_count)

        # 文件模式：文件/目录选择（通过 visible 控制显示）
        self._file_row = QHBoxLayout()
        layout.addLayout(self._file_row)

        self._file_row.addWidget(QLabel("文件/目录："))
        self._file_input = QLineEdit()
        self._file_input.setPlaceholderText("选择文件或目录")
        self._file_row.addWidget(self._file_input, 1)

        btn_browse = QPushButton("浏览")
        btn_browse.clicked.connect(self._on_browse_file)
        self._file_row.addWidget(btn_browse)

        # 文件模式：兑换码数量 + 显示按钮
        self._code_row = QHBoxLayout()
        layout.addLayout(self._code_row)

        self._code_row.addWidget(QLabel("兑换码数量："))
        self._code_count = QSpinBox()
        self._code_count.setRange(1, 1000)
        self._code_count.setValue(5)
        self._code_row.addWidget(self._code_count)


        self._code_row.addStretch(1)

        # 服务器设置（同一块）
        row_server = QHBoxLayout()
        layout.addLayout(row_server)

        row_server.addWidget(QLabel("端口："))
        self._port_input = QLineEdit("80")
        self._port_input.setFixedWidth(80)
        row_server.addWidget(self._port_input)

        self._no_browser = QCheckBox("不自动打开浏览器")
        row_server.addWidget(self._no_browser)

        self._password_protected = QCheckBox("启用管理员密码")
        row_server.addWidget(self._password_protected)

        row_server.addStretch(1)

        # 默认隐藏文件模式行
        self._set_files_rows_visible(False)

        # 按钮区
        btn_row = QHBoxLayout()
        
        self._start_btn = QPushButton("启动服务器")
        self._start_btn.clicked.connect(self._on_toggle_server)
        btn_row.addWidget(self._start_btn)
        
        self._open_btn = QPushButton("打开抽奖页面")
        self._open_btn.clicked.connect(self._on_open_browser)
        self._open_btn.setEnabled(False)
        btn_row.addWidget(self._open_btn)

        self._btn_codes = QPushButton("抽奖码")
        self._btn_codes.setEnabled(False)  # 未启动服务器前禁用
        self._btn_codes.clicked.connect(self._on_show_codes_clicked)
        btn_row.addWidget(self._btn_codes)
        
        btn_row.addStretch(1)
        layout.addLayout(btn_row)
        
        # 状态信息
        self._status = QLabel("状态：未启动")
        layout.addWidget(self._status)
        
        # 日志输出
        self._log = QLabel()
        self._log.setWordWrap(True)
        # 允许选择/复制文本（PySide6 需要传 Qt.TextInteractionFlag 枚举）
        try:
            from ..core.compatibility import Qt

            self._log.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        except Exception:
            pass
        layout.addWidget(self._log, 1)
        
        # 更新UI状态
        self._update_items_count()
        self._update_ui_state()

    def _on_mode_changed(self, checked: bool):
        """切换抽奖模式"""
        # toggled 信号会对“选中”和“取消选中”两个按钮都触发
        # 我们只在按钮被“选中”时执行逻辑，避免重复
        if not checked:
            return

        is_normal = self._mode_normal.isChecked()
        self._set_files_rows_visible(not is_normal)
        self._update_ui_state()  # 更新控件的启用/禁用状态

    def _on_manage_items(self):
        """打开管理抽奖元素对话框"""
        dlg = PickItemsManagerDialog(self)
        dlg.exec()
        self._update_items_count()

    def _on_show_codes_clicked(self) -> None:
        """显示本次生成的抽奖码（仅文件模式且服务运行中）。"""

        if not self._server_running:
            return
        if self._mode_normal.isChecked():
            return

        # 始终从 dump 文件读取（避免显示上一次缓存）
        codes_text = ""
        try:
            if os.path.exists(self._codes_dump_file):
                with open(self._codes_dump_file, "r", encoding="utf-8") as f:
                    codes_text = f.read().strip()
        except Exception:
            codes_text = ""

        if not codes_text:
            QMessageBox.information(self, "抽奖码", "当前没有可显示的抽奖码（可能未生成）。")
            return

        # 美化展示
        pretty = "已生成抽奖码：\n\n" + "\n".join([f"  {c}" for c in codes_text.splitlines() if c.strip()])
        PickCodesDialog(pretty, self).exec()

    def _update_items_count(self):
        """更新抽奖元素数量显示"""
        try:
            cfg = load_json_config(get_config_path("fcbyk", "pick.json"), {"items": []})
            count = len(cfg.get("items", []))
            self._items_count.setText(str(count))
        except Exception:
            self._items_count.setText("-")

    def _on_browse_file(self):
        """浏览文件或目录"""
        path = QFileDialog.getExistingDirectory(self, "选择目录") if self._mode_files.isChecked() else \
               QFileDialog.getOpenFileName(self, "选择文件")[0]
        if path:
            self._file_input.setText(path)

    def _on_toggle_server(self):
        """启动/停止服务器"""
        if self._server_running:
            self._stop_server()
        else:
            self._start_server()

    def _start_server(self):
        """启动抽奖服务器"""
        # 获取端口
        try:
            port = int(self._port_input.text().strip())
            if not (0 < port <= 65535):
                raise ValueError("端口号必须在1-65535之间")
        except ValueError as e:
            QMessageBox.warning(self, "参数错误", f"无效的端口号: {e}")
            return

        # 检查端口占用
        try:
            ensure_port_available(port, host="0.0.0.0")
        except OSError as e:
            QMessageBox.critical(self, "端口被占用", f"端口 {port} 已被占用，请更换端口后重试。\n\n{str(e)}")
            return

        # 获取其他参数
        no_browser = self._no_browser.isChecked()
        use_password = self._password_protected.isChecked()
        
        # 根据模式准备参数
        is_normal_mode = self._mode_normal.isChecked()
        
        if is_normal_mode:
            # 检查是否有抽奖元素
            cfg = load_json_config(get_config_path("fcbyk", "pick.json"), {"items": []})
            if not cfg.get("items"):
                QMessageBox.warning(self, "无法启动", "请先添加抽奖元素！")
                return
            
            # 启动普通模式
            self._start_server_process(port, no_browser, use_password)
        else:
            # 文件模式
            file_path = self._file_input.text().strip()
            if not file_path:
                QMessageBox.warning(self, "参数错误", "请选择文件或目录")
                return
            
            if not os.path.exists(file_path):
                QMessageBox.warning(self, "错误", f"文件或目录不存在: {file_path}")
                return
            
            # 启动文件模式（兑换码生成交由子进程；show_codes 会写到日志文件）
            self._start_server_process(port, no_browser, use_password, file_path, None)

    def _start_server_process(self, port, no_browser, use_password, files_root=None, codes=None):
        """启动服务器子进程（方案 A：直接调用 start_web_server）。"""

        # 管理员密码：GUI 下不走 click 交互，直接弹窗输入（可空 -> 默认 123456）
        admin_password = "123456"
        if use_password:
            pw = self._prompt_password(default_value="123456")
            if pw is None:
                return
            admin_password = pw

        gen_codes = int(self._code_count.value()) if files_root else 0
        # 兑换码弹窗显示：由 GUI 读取 dump 文件弹窗展示；这里不再提供“显示兑换码”选项
        show_codes = False

        # 启动前清理旧的抽奖码文件，避免新进程没来得及写入时读到旧内容
        try:
            if files_root and os.path.exists(self._codes_dump_file):
                os.remove(self._codes_dump_file)
        except Exception:
            pass

        code = (
            "from fcbyk.gui.ui.pick_page import _run_pick_server_process; "
            f"_run_pick_server_process({port!r}, {bool(no_browser)!r}, {files_root!r}, {gen_codes!r}, {show_codes!r}, {self._codes_dump_file!r}, {admin_password!r})"
        )

        try:
            # 日志写到文件（避免 PIPE 堵塞）
            try:
                log_fp = open(self._server_log_file, "a", encoding="utf-8")
            except Exception:
                log_fp = subprocess.DEVNULL

            creationflags = 0
            if sys.platform == "win32":
                creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0)

            self._server_proc = subprocess.Popen(
                [sys.executable, "-c", code],
                stdin=subprocess.DEVNULL,
                stdout=log_fp,
                stderr=log_fp,
                creationflags=creationflags,
                close_fds=(sys.platform != "win32"),
            )

            # 启动前清理旧的抽奖码文件，避免显示上一次的内容
            try:
                if files_root and os.path.exists(self._codes_dump_file):
                    os.remove(self._codes_dump_file)
            except Exception:
                pass

            self._server_running = True
            self._update_ui_state()

            local_url = f"http://127.0.0.1:{port}"
            network_url = f"http://{self._get_local_ip()}:{port}"

            self._status.setText(f"状态：运行中（端口: {port}，PID: {self._server_proc.pid}）")
            self._log.setText(
                f"抽奖服务器已启动（后台进程）。\n"
                f"本地访问: {local_url}\n"
                f"局域网访问: {network_url}\n"
                f"管理后台: {network_url}/admin\n"
                + (f"文件抽奖入口: {network_url}/f\n" if files_root else "")
                + f"日志文件: {self._server_log_file}\n"
            )


        except Exception as e:
            self._server_error = str(e)
            self._update_ui_state()
            QMessageBox.critical(self, "启动失败", f"无法启动服务器: {e}")

    def _stop_server(self):
        """停止服务器"""
        if not self._server_running or not self._server_proc:
            return
        
        try:
            # 终止子进程
            self._server_proc.terminate()
            try:
                self._server_proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                self._server_proc.kill()
                self._server_proc.wait()
                
            self._log.setText(self._log.text() + "\n\n服务器已停止。")
            
        except Exception as e:
            self._log.setText(self._log.text() + f"\n\n停止服务器时出错: {e}")
        finally:
            self._server_proc = None
            self._server_running = False
            self._update_ui_state()
            self._status.setText("状态：已停止")

    def _on_open_browser(self):
        """在浏览器中打开抽奖页面"""
        if not self._server_running:
            return
            
        try:
            port = int(self._port_input.text().strip())
            url = f"http://127.0.0.1:{port}"
            webbrowser.open(url)
        except Exception as e:
            QMessageBox.warning(self, "错误", f"无法打开浏览器: {e}")

    def _get_local_ip(self) -> str:
        """获取本地IP地址"""
        try:
            import socket
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "<本地IP>"

    def _prompt_password(self, default_value: str = "123456") -> Optional[str]:
        """弹窗输入管理员密码。

        返回：
        - str : 用户输入（为空则返回 default_value）
        - None: 用户取消
        """

        box = QMessageBox(self)
        box.setWindowTitle("管理员密码")
        box.setText(f"请输入管理员密码（留空则使用默认：{default_value}）")
        box.setIcon(QMessageBox.Icon.Question)

        inp = QLineEdit(box)
        inp.setEchoMode(QLineEdit.EchoMode.Password)
        inp.setPlaceholderText(default_value)
        try:
            inp.setMinimumWidth(260)
        except Exception:
            pass

        try:
            box.layout().addWidget(inp)
        except Exception:
            pass

        box.setStandardButtons(QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
        ret = box.exec()
        if ret != QMessageBox.StandardButton.Ok:
            return None

        return (inp.text() or "").strip() or default_value

    def _update_ui_state(self):
        """更新UI状态"""
        is_running = self._server_running
        
        # 更新按钮状态
        self._start_btn.setText("停止服务器" if is_running else "启动服务器")
        self._open_btn.setEnabled(is_running)
        
        # 禁用/启用控件
        self._mode_normal.setEnabled(not is_running)
        self._mode_files.setEnabled(not is_running)
        self._port_input.setReadOnly(is_running)
        self._no_browser.setEnabled(not is_running)
        self._password_protected.setEnabled(not is_running)
        
        # 文件模式控件
        if hasattr(self, "_file_input"):
            self._file_input.setReadOnly(is_running)
            self._file_input.setEnabled((not is_running) and (not self._mode_normal.isChecked()))
        if hasattr(self, "_code_count"):
            self._code_count.setEnabled((not is_running) and (not self._mode_normal.isChecked()))

        # 抽奖码按钮：仅在“文件模式且服务运行中”可用
        if hasattr(self, "_btn_codes"):
            self._btn_codes.setEnabled(bool(is_running) and (not self._mode_normal.isChecked()))

    def stop_if_running(self):
        """如果服务器正在运行，则停止"""
        if self._server_running and self._server_proc:
            self._stop_server()

    def closeEvent(self, event):
        """窗口关闭事件"""
        self.stop_if_running()
        event.accept()

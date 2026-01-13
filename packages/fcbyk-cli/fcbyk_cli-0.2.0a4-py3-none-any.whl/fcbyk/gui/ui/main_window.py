"""主窗口实现。"""

import sys

from ..core.compatibility import (
    QAction,
    QMainWindow,
    QMenu,
    QSystemTrayIcon,
    QTabWidget,
    QVBoxLayout,
    QWidget,
    Qt,
)

from .slide_page import SlidePage
from .lansend_page import LansendPage
from .pick_page import PickPage
from .resources import create_app_icon


class MainWindow(QMainWindow):
    """主窗口。

    本窗口包含 GUI 的主框架（托盘、窗口激活等），具体命令页面（如 LANSend）
    已拆分到独立模块，避免 main_window.py 继续膨胀。

    关闭按钮行为：默认不退出，而是隐藏到系统托盘；
    仅从托盘菜单选择“退出”才会真正关闭进程（类似网易云音乐）。
    """

    def __init__(self):
        super().__init__()

        self._is_quitting = False

        self.setWindowTitle("fcbyk CLI - GUI")

        # 限制窗口尺寸范围（避免过大/过小），同时不使用“最大化”
        self.resize(640, 420)
        self.setMinimumSize(640, 420)
        self.setMaximumSize(960, 700)

        # 取消标题栏最大化按钮（也会阻止标题栏双击最大化）
        self.setWindowFlag(Qt.WindowType.WindowMaximizeButtonHint, False)

        # 标题栏图标建议使用 16/24/32 等小尺寸，否则某些系统主题会出现裁剪。
        self.setWindowIcon(create_app_icon(prefer_titlebar_size=24))

        # 系统托盘
        self._setup_tray_icon()

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        # 顶部 Tabs
        self._tabs = QTabWidget(self)
        layout.addWidget(self._tabs)

        # 页面：后续其它命令页面可按相同模式新增
        self._lansend_page = LansendPage(self)
        self._slide_page = SlidePage(self)
        self._pick_page = PickPage(self)

        self._tabs.addTab(self._lansend_page, "LANSend")
        self._tabs.addTab(self._slide_page, "Slide")
        self._tabs.addTab(self._pick_page, "Pick")

    def _setup_tray_icon(self):
        """初始化系统托盘与菜单。"""
        if not QSystemTrayIcon.isSystemTrayAvailable():
            self._tray_icon = None
            return

        self._tray_icon = QSystemTrayIcon(self)
        self._tray_icon.setIcon(create_app_icon(prefer_titlebar_size=24))
        self._tray_icon.setToolTip("fcbyk CLI - GUI")

        menu = QMenu()

        action_show = QAction("显示主窗口", self)
        action_show.triggered.connect(self.show_and_raise)
        menu.addAction(action_show)

        menu.addSeparator()

        action_quit = QAction("退出", self)
        action_quit.triggered.connect(self._on_quit_request)
        menu.addAction(action_quit)

        self._tray_icon.setContextMenu(menu)

        # 双击托盘图标：显示窗口（各平台习惯略有差异，这里用 Activated 兼容）
        self._tray_icon.activated.connect(self._on_tray_activated)

        self._tray_icon.show()

    def _on_tray_activated(self, reason):
        # QSystemTrayIcon.ActivationReason
        try:
            trigger = QSystemTrayIcon.ActivationReason.Trigger
            double_click = QSystemTrayIcon.ActivationReason.DoubleClick
        except Exception:  # pragma: no cover
            trigger = QSystemTrayIcon.Trigger
            double_click = QSystemTrayIcon.DoubleClick

        if reason in (trigger, double_click):
            self.show_and_raise()

    def _on_quit_request(self):
        """真正退出前：如果页面有后台任务，先停止。"""
        try:
            # 目前：LANSend + Slide
            if getattr(self, "_lansend_page", None) is not None:
                self._lansend_page.stop_if_running()
            if getattr(self, "_slide_page", None) is not None:
                # Slide 运行在子进程中，这里确保退出前停止子进程
                self._slide_page.stop_if_running()
            if getattr(self, "_pick_page", None) is not None:
                self._pick_page.stop_if_running()
        except Exception:
            pass

        self.quit_from_tray()

    def quit_from_tray(self):
        """从托盘菜单触发的真正退出。"""
        self._is_quitting = True
        # 先隐藏托盘图标，避免退出后残留
        if getattr(self, "_tray_icon", None) is not None:
            try:
                self._tray_icon.hide()
            except Exception:
                pass
        # 直接退出 Qt 事件循环（更可靠，避免仅 close 窗口但进程仍存活）
        try:
            from ..core.compatibility import QApplication

            app = QApplication.instance()
            if app is not None:
                app.quit()
                return
        except Exception:
            pass

        self.close()

    def closeEvent(self, event):  # noqa: N802
        """拦截窗口关闭按钮：默认隐藏到托盘。"""
        if self._is_quitting or self._tray_icon is None:
            event.accept()
            return

        event.ignore()
        self.hide()

        # 第一次提示用户已最小化到托盘
        if not getattr(self, "_tray_notice_shown", False):
            self._tray_notice_shown = True
            try:
                info = QSystemTrayIcon.MessageIcon.Information
            except Exception:  # pragma: no cover
                info = QSystemTrayIcon.Information

            self._tray_icon.showMessage(
                "fcbyk CLI - GUI",
                "程序已缩小到系统托盘。\n在托盘图标右键选择“退出”可完全关闭。",
                info,
                3000,
            )

    def _force_foreground_windows(self):
        """Windows 专用：使用 Win32 API 尽力将窗口置前。"""
        try:
            import ctypes
            from ctypes import wintypes

            user32 = ctypes.windll.user32
            kernel32 = ctypes.windll.kernel32

            SW_RESTORE = 9
            FLASHW_ALL = 3
            FLASHW_TIMERNOFG = 12

            class FLASHWINFO(ctypes.Structure):
                _fields_ = [
                    ("cbSize", wintypes.UINT),
                    ("hwnd", wintypes.HWND),
                    ("dwFlags", wintypes.DWORD),
                    ("uCount", wintypes.UINT),
                    ("dwTimeout", wintypes.DWORD),
                ]

            hwnd = int(self.winId())
            fg_win = user32.GetForegroundWindow()
            fg_tid = user32.GetWindowThreadProcessId(fg_win, None)
            our_tid = kernel32.GetCurrentThreadId()

            user32.AttachThreadInput(fg_tid, our_tid, True)
            user32.AllowSetForegroundWindow(-1)  # ASFW_ANY

            user32.ShowWindow(hwnd, SW_RESTORE)
            user32.SetForegroundWindow(hwnd)
            user32.SetFocus(hwnd)

            user32.AttachThreadInput(fg_tid, our_tid, False)

            if user32.GetForegroundWindow() != hwnd:
                info = FLASHWINFO(
                    cbSize=ctypes.sizeof(FLASHWINFO),
                    hwnd=hwnd,
                    dwFlags=FLASHW_ALL | FLASHW_TIMERNOFG,
                    uCount=0,
                    dwTimeout=0,
                )
                user32.FlashWindowEx(ctypes.byref(info))

        except Exception:
            self.raise_()
            self.activateWindow()

    def show_and_raise(self):
        """显示并激活窗口。

        Windows 上由于前台焦点限制，尽力置前；失败时会闪烁任务栏图标。
        """
        if self.isMinimized():
            self.showNormal()

        self.show()

        if sys.platform == "win32":
            self._force_foreground_windows()
        else:
            self.raise_()
            self.activateWindow()

"""GUI 模块 - 提供图形化界面"""

try:
    from .app import HAS_GUI, kill_gui, run_gui_standalone, show_gui

    if HAS_GUI:
        __all__ = ["HAS_GUI", "show_gui", "kill_gui", "run_gui_standalone"]
    else:
        __all__ = ["HAS_GUI"]
except ImportError:
    __all__ = []


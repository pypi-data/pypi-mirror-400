"""GUI 包入口。

用于 `python -m fcbyk.gui` 启动 GUI。

注意：请不要在这里 import fcbyk.gui.app 并再次执行同名模块，避免 runpy 报
"found in sys.modules ... prior to execution" 的警告。

我们直接调用 GUI 的实际入口函数。
"""

# 避免 runpy 对同名模块的二次执行：这里不再触发 `python -m fcbyk.gui.app`
from .app import run_gui_standalone

run_gui_standalone()

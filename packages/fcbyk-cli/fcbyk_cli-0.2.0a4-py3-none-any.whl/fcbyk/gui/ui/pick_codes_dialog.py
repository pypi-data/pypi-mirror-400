"""Pick 兑换码显示子窗口。

说明：
- 该窗口只负责展示兑换码文本（通常来自日志/主进程生成）
- 当前实现用于 GUI 启动服务后展示本次生成的兑换码
"""

from ..core.compatibility import QDialog, QLabel, QPushButton, QVBoxLayout


class PickCodesDialog(QDialog):
    def __init__(self, codes_text: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("兑换码")
        self.resize(420, 360)

        layout = QVBoxLayout()
        self.setLayout(layout)

        label = QLabel(codes_text or "(无)")
        label.setWordWrap(True)
        # 允许选择/复制
        try:
            from ..core.compatibility import Qt

            label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        except Exception:
            pass
        layout.addWidget(label, 1)

        btn = QPushButton("关闭")
        btn.clicked.connect(self.accept)
        layout.addWidget(btn)


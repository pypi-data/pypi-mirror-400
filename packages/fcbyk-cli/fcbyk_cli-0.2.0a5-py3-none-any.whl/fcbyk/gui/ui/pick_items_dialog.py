"""Pick 抽奖元素管理子窗口。

功能：
- 从 pick.json 读取/保存 items
- 列表展示、添加、删除、清空

说明：
- 仅负责 items 管理，不负责启动服务器
- 设计为 Dialog，供 PickPage 弹出
"""

from ..core.compatibility import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)

from fcbyk.utils.config import get_config_path, load_json_config, save_config


class PickItemsManagerDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("管理抽奖元素")
        self.resize(520, 420)

        self._config_file = get_config_path("fcbyk", "pick.json")
        self._default_config = {"items": []}

        root = QVBoxLayout()
        self.setLayout(root)

        title = QLabel("抽奖元素（items）")
        title.setStyleSheet("font-size: 14px; font-weight: 600;")
        root.addWidget(title)

        self._list = QListWidget()
        root.addWidget(self._list, 1)

        # 添加行
        row_add = QHBoxLayout()
        root.addLayout(row_add)

        row_add.addWidget(QLabel("新增："))
        self._input = QLineEdit()
        self._input.setPlaceholderText("输入要加入的元素，回车或点【添加】")
        self._input.returnPressed.connect(self._on_add_clicked)
        row_add.addWidget(self._input, 1)

        btn_add = QPushButton("添加")
        btn_add.clicked.connect(self._on_add_clicked)
        row_add.addWidget(btn_add)

        # 按钮区
        row_btn = QHBoxLayout()
        root.addLayout(row_btn)

        btn_remove = QPushButton("删除选中")
        btn_remove.clicked.connect(self._on_remove_selected)
        row_btn.addWidget(btn_remove)

        btn_clear = QPushButton("清空")
        btn_clear.clicked.connect(self._on_clear)
        row_btn.addWidget(btn_clear)

        row_btn.addStretch(1)

        btn_close = QPushButton("关闭")
        btn_close.clicked.connect(self.accept)
        row_btn.addWidget(btn_close)

        self._load_items_to_ui()

    # -----------------
    # data
    # -----------------

    def _load_config(self) -> dict:
        return load_json_config(self._config_file, self._default_config)

    def _save_items(self, items: list) -> None:
        cfg = self._load_config()
        cfg["items"] = items
        save_config(cfg, self._config_file)

    def _load_items_to_ui(self) -> None:
        self._list.clear()
        cfg = self._load_config()
        items = cfg.get("items", []) or []
        for it in items:
            self._list.addItem(str(it))

    def _current_items(self) -> list:
        items = []
        for i in range(self._list.count()):
            items.append(self._list.item(i).text())
        return items

    # -----------------
    # handlers
    # -----------------

    def _on_add_clicked(self) -> None:
        text = (self._input.text() or "").strip()
        if not text:
            return

        items = self._current_items()
        if text in items:
            QMessageBox.information(self, "提示", f"已存在：{text}")
            return

        self._list.addItem(text)
        self._input.setText("")
        self._save_items(self._current_items())

    def _on_remove_selected(self) -> None:
        row = self._list.currentRow()
        if row < 0:
            QMessageBox.information(self, "提示", "请先选中要删除的元素")
            return

        it = self._list.item(row)
        name = it.text() if it else ""
        ret = QMessageBox.question(self, "确认删除", f"确定删除：{name} ？")
        if ret != QMessageBox.StandardButton.Yes:
            return

        self._list.takeItem(row)
        self._save_items(self._current_items())

    def _on_clear(self) -> None:
        ret = QMessageBox.question(self, "确认清空", "确定清空所有抽奖元素？")
        if ret != QMessageBox.StandardButton.Yes:
            return

        self._list.clear()
        self._save_items([])


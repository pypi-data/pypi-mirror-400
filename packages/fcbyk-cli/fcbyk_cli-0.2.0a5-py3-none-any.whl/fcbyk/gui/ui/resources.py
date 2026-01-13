"""GUI 资源（图标等）。"""

import os
import sys
from typing import Optional

from ..core.compatibility import (
    QColor,
    QFont,
    QIcon,
    QPainter,
    QPixmap,
    QSvgRenderer,
    QByteArray,
    Qt,
)


def create_app_icon(*, prefer_titlebar_size=None) -> QIcon:
    # type: (Optional[int]) -> QIcon
    """创建应用图标。

    优先加载 `favicon.png` / `favicon.svg`，否则程序生成 `:(` 图标。

    Args:
        prefer_titlebar_size: 若传入（例如 24），会将该尺寸作为“优先”加入 QIcon。
            某些平台/主题会优先选用第一个匹配或最接近的尺寸，提前加入小尺寸
            可以减少标题栏图标被裁剪的概率。
    """
    base_dir = os.path.dirname(__file__)
    # resources.py 位于 ui/，favicon.png 位于 gui/ 目录
    base_dir = os.path.dirname(base_dir)
    
    png_file = os.path.join(base_dir, "assets", "icon.png")
    if os.path.exists(png_file):
        src_pm = QPixmap(png_file)
        if not src_pm.isNull():
            icon = QIcon()
            sizes = [16, 24, 32, 48, 64, 128, 256]
            if prefer_titlebar_size and prefer_titlebar_size in sizes:
                sizes = [prefer_titlebar_size] + [s for s in sizes if s != prefer_titlebar_size]
            for size in sizes:
                pm = src_pm.scaled(
                    size,
                    size,
                    Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                    Qt.TransformationMode.SmoothTransformation,
                )
                x = max(0, (pm.width() - size) // 2)
                y = max(0, (pm.height() - size) // 2)
                pm_sq = pm.copy(x, y, size, size)
                icon.addPixmap(pm_sq)
            if not icon.isNull():
                return icon

    svg_file = os.path.join(base_dir, "favicon.svg")
    if os.path.exists(svg_file):
        try:
            with open(svg_file, "rb") as f:
                svg_bytes = f.read()
            renderer = QSvgRenderer(QByteArray(svg_bytes))
            if renderer.isValid():
                icon = QIcon()
                sizes = [16, 24, 32, 48, 64, 128, 256]
                if prefer_titlebar_size and prefer_titlebar_size in sizes:
                    sizes = [prefer_titlebar_size] + [s for s in sizes if s != prefer_titlebar_size]
                for size in sizes:
                    pixmap = QPixmap(size, size)
                    pixmap.fill(QColor(0, 0, 0, 0))
                    painter = QPainter(pixmap)
                    renderer.render(painter)
                    painter.end()
                    icon.addPixmap(pixmap)
                if not icon.isNull():
                    return icon
        except Exception:
            pass

    icon = QIcon()

    try:
        render_hint = QPainter.RenderHint.Antialiasing
    except AttributeError:  # pragma: no cover
        render_hint = QPainter.Antialiasing

    sizes = [16, 24, 32, 48, 64, 128, 256]
    if prefer_titlebar_size and prefer_titlebar_size in sizes:
        sizes = [prefer_titlebar_size] + [s for s in sizes if s != prefer_titlebar_size]

    for size in sizes:
        pixmap = QPixmap(size, size)
        pixmap.fill(QColor(255, 255, 255))

        painter = QPainter(pixmap)
        painter.setRenderHint(render_hint)

        font = QFont("Consolas" if sys.platform == "win32" else "Monospace")
        font.setBold(True)
        font_size = int(size * 0.55)
        font.setPixelSize(font_size)
        painter.setFont(font)

        painter.setPen(QColor(0, 0, 0))

        text = ":("
        font_metrics = painter.fontMetrics()
        try:
            text_width = font_metrics.horizontalAdvance(text)
        except AttributeError:  # pragma: no cover
            text_width = font_metrics.width(text)
        text_height = font_metrics.height()
        x = (size - text_width) // 2
        y = (size + text_height) // 2 - font_metrics.descent()

        painter.drawText(x, y, text)
        painter.end()

        icon.addPixmap(pixmap)

    return icon


"""popup 业务逻辑层

负责弹窗展示的核心逻辑（Tk 窗口创建、随机位置/颜色/提示等）。

"""

import random
import threading
import time
from dataclasses import dataclass
from typing import Iterable, List, Optional

import tkinter as tk


DEFAULT_TIPS: List[str] = [
    '多喝水哦~', '保持微笑呀', '每天都要元气满满',
    '记得吃水果', '保持好心情', '好好爱自己', '我想你了',
    '梦想成真', '期待下一次见面', '金榜题名',
    '顺顺利利', '早点休息', '愿所有烦恼都消失',
    '别熬夜', '今天过得开心嘛', '天冷了，多穿衣服',
]


@dataclass(frozen=True)
class PopupOptions:
    title: str = '温馨提示'
    numbers: int = 20
    tips: Optional[Iterable[str]] = None
    delay_seconds: float = 0.005


class PopupService:
    """弹窗服务"""

    BG_COLORS = [
        'lightpink', 'skyblue', 'lightgreen', 'lavender',
        'lightyellow', 'plum', 'coral', 'bisque', 'aquamarine',
        'mistyrose', 'honeydew', 'lavenderblush', 'oldlace',
    ]

    def show_one(self, title: str, tips: List[str]) -> None:
        window = tk.Tk()

        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()

        window_width = 250
        window_height = 60
        x = random.randrange(0, max(1, screen_width - window_width))
        y = random.randrange(0, max(1, screen_height - window_height))

        window.title(title)
        window.geometry(f"{window_width}x{window_height}+{x}+{y}")

        tip = random.choice(tips) if tips else ''
        bg = random.choice(self.BG_COLORS)

        tk.Label(
            window,
            text=tip,
            bg=bg,
            font=('微软雅黑', 16),
            width=30,
            height=3,
        ).pack()

        window.attributes('-topmost', True)
        window.mainloop()

    def spawn_many(self, opts: PopupOptions) -> List[threading.Thread]:
        tips = list(opts.tips) if opts.tips else list(DEFAULT_TIPS)

        threads: List[threading.Thread] = []
        for i in range(opts.numbers):
            t = threading.Thread(target=self.show_one, args=(opts.title, tips))
            threads.append(t)
            time.sleep(opts.delay_seconds)
            t.start()

        return threads


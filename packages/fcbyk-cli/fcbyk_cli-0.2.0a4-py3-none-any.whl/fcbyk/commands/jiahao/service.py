"""
jiahao 业务逻辑层

类:
- DisplayMode: 显示模式枚举（binary/code/matrix/glitch）
- TerminalSize: 终端尺寸数据类（columns, rows）
  - detect() -> TerminalSize: 自动检测终端尺寸
- TerminalControl: 终端 ANSI 控制封装
  - clear_screen(): 清屏
  - hide_cursor(): 隐藏光标
  - show_cursor(): 显示光标
  - move_cursor(x, y): 移动光标到指定位置
- HackerTerminal: 黑客终端模拟器核心类
  - run(): 主运行入口
  - show_completion_screen(): 显示完成界面
  - _setup(): 初始化终端状态
  - _main_loop(): 主渲染循环
  - _cleanup(): 清理终端状态
  - _generate_screen() -> List[str]: 根据模式生成屏幕内容
  - _render_screen(lines, elapsed): 渲染屏幕内容到终端
  - _render_status(elapsed): 渲染底部状态栏
  - _generate_binary_screen() -> List[str]: 生成二进制雨效果
  - _generate_matrix_screen() -> List[str]: 生成矩阵字符效果
  - _generate_code_screen() -> List[str]: 生成代码片段效果
  - _generate_glitch_screen() -> List[str]: 生成故障艺术效果

函数:
- enable_windows_ansi() -> bool: 在 Windows 上启用 ANSI 支持
"""

import random
import sys
import time
from dataclasses import dataclass
from enum import Enum
from threading import Event
from typing import List


def enable_windows_ansi():
    """在 Windows 上尝试启用 ANSI 支持（可选依赖 colorama）"""
    try:
        import colorama
        if sys.platform == 'win32':
            # colorama 0.4.6+ 使用 just_fix_windows_console()
            # 旧版本使用 init()
            if hasattr(colorama, 'just_fix_windows_console'):
                colorama.just_fix_windows_console()
            else:
                colorama.init()
        return True
    except (ImportError, AttributeError):
        return False


class DisplayMode(str, Enum):
    BINARY = 'binary'
    CODE = 'code'
    MATRIX = 'matrix'
    GLITCH = 'glitch'


@dataclass
class TerminalSize:
    columns: int
    rows: int

    @classmethod
    def detect(cls):
        try:
            import shutil
            size = shutil.get_terminal_size()
            return cls(size.columns, size.lines)
        except Exception:
            return cls(80, 24)


class TerminalControl:
    """终端控制辅助类，处理 ANSI 控制序列"""

    def __init__(self, ansi_enabled=True):
        self.ansi_enabled = bool(ansi_enabled) and sys.stdout.isatty()
        self._original_stdout = sys.stdout

    def clear_screen(self):
        if not self.ansi_enabled:
            return
        self._write('\033[2J\033[H')

    def hide_cursor(self):
        if not self.ansi_enabled:
            return
        self._write('\033[?25l')

    def show_cursor(self):
        if not self.ansi_enabled:
            return
        self._write('\033[?25h')

    def move_cursor(self, x, y):
        if not self.ansi_enabled:
            return
        self._write('\033[{y};{x}H'.format(y=y, x=x))

    def _write(self, text):
        self._original_stdout.write(text)
        self._original_stdout.flush()


class HackerTerminal:
    """黑客终端模拟器核心类"""

    def __init__(
        self,
        mode=DisplayMode.BINARY,
        duration=30.0,
        speed=0.05,
        density=0.7,
        ansi_enabled=True,
    ):
        self.mode = mode
        self.duration = max(1.0, float(duration))
        self.speed = max(0.01, min(float(speed), 1.0))
        self.density = max(0.1, min(float(density), 1.0))
        self.ansi_enabled = bool(ansi_enabled)

        self.running = False
        self.start_time = 0.0
        self.terminal = TerminalControl(ansi_enabled)
        self.size = TerminalSize.detect()
        self.stop_event = Event()

        # 各模式使用的字符集
        self.binary_chars = "01"
        self.hex_chars = "0123456789ABCDEF"
        self.matrix_chars = "アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲン"
        self.code_chars = "{}[]()<>;:=+-*/&|!~#@%$_"
        self.glitch_chars = "░▒▓█▀▄▌▐■□▲►▼◄◆◇○●◎☆★☯☮☣☢☠♛♕♔♚"
        self.alphanum_chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

        # 模拟入侵的系统名称列表
        self.systems = [
            "GOV-SECURE-NET", "PENTAGON-ALPHA", "CIA-CLOUD-7",
            "NSA-QUANTUM", "MILITARY-GRID", "SWIFT-CORE",
            "NASA-JPL-MAIN", "TESLA-AI-CENTRAL", "SPACEX-COMM",
            "GOOGLE-DEEP-MIND", "FACEBOOK-META-VR", "APPLE-SECURE",
            "AMAZON-AWS-CONTROL", "MICROSOFT-AZURE-CORE",
            "TOR-HIDDEN-SERVICE", "DARKNET-EXCHANGE",
        ]

    def run(self):
        try:
            self._setup()
            self._main_loop()
        except KeyboardInterrupt:
            pass
        finally:
            self._cleanup()

    def _setup(self):
        self.running = True
        self.start_time = time.time()
        self.terminal.clear_screen()
        self.terminal.hide_cursor()

    def _main_loop(self):
        while self.running and not self.stop_event.is_set():
            elapsed = time.time() - self.start_time
            if elapsed >= self.duration:
                break

            screen = self._generate_screen()
            self._render_screen(screen, elapsed)
            time.sleep(self.speed)

    def _cleanup(self):
        self.running = False
        self.stop_event.set()
        self.terminal.show_cursor()
        self.terminal.clear_screen()

    def _generate_screen(self):
        if self.mode == DisplayMode.BINARY:
            return self._generate_binary_screen()
        if self.mode == DisplayMode.MATRIX:
            return self._generate_matrix_screen()
        if self.mode == DisplayMode.CODE:
            return self._generate_code_screen()
        if self.mode == DisplayMode.GLITCH:
            return self._generate_glitch_screen()
        return self._generate_binary_screen()

    def _render_screen(self, lines, elapsed):
        if not self.ansi_enabled:
            print("\n".join(lines))
            return

        self.terminal.move_cursor(1, 1)

        cols = self.size.columns
        rows = self.size.rows
        pad_width = max(0, cols - 1)
        content_height = max(0, rows - 2)

        # 输出内容行
        for i in range(min(len(lines), content_height)):
            sys.stdout.write(lines[i].ljust(pad_width) + '\n')

        # 补足空行清除上一帧残留
        remaining = content_height - min(len(lines), content_height)
        if remaining > 0:
            blank = ' ' * pad_width + '\n'
            for _ in range(remaining):
                sys.stdout.write(blank)

        self._render_status(elapsed)
        sys.stdout.flush()

    def _render_status(self, elapsed):
        if not self.ansi_enabled:
            return

        rows = self.size.rows
        cols = self.size.columns

        # 倒数第三行：系统信息
        if rows > 2:
            self.terminal.move_cursor(1, rows - 2)
            system_info = "\033[0;36mTARGET: {target:<20} | BREACH: {breach:5.1f}% | THREAT: {threat:>3}%\033[0m".format(
                target=random.choice(self.systems),
                breach=min(100.0, (elapsed / self.duration) * 100.0),
                threat=random.randint(1, 100),
            )
            sys.stdout.write(system_info.ljust(max(0, cols - 1)))

        # 倒数第二行：进度条
        if rows > 1:
            self.terminal.move_cursor(1, rows - 1)
            progress = min(elapsed / self.duration, 1.0)
            bar_width = max(20, cols - 20)
            filled = int(bar_width * progress)
            bar = "█" * filled + "░" * (bar_width - filled)

            speed_txt = "{fps:.1f}FPS".format(fps=(1.0 / self.speed)) if self.speed > 0 else "MAX"
            status = random.choice(["ACTIVE", "RUNNING", "SCANNING", "DECRYPTING"])

            progress_line = "\033[1;37m[{bar}] {pct:5.1f}% | {elapsed:5.1f}s/{dur}s | {status:<12} | {speed}\033[0m".format(
                bar=bar,
                pct=progress * 100.0,
                elapsed=elapsed,
                dur=int(self.duration),
                status=status,
                speed=speed_txt,
            )
            sys.stdout.write(progress_line.ljust(max(0, cols - 1)))

    def _generate_binary_screen(self):
        cols = self.size.columns
        rows = self.size.rows - 2
        screen = []

        for _ in range(rows):
            line = []
            for _ in range(cols):
                if random.random() < self.density:
                    char = random.choice(self.binary_chars)
                    if random.random() < 0.1:
                        line.append("\033[1;32m{c}\033[0m".format(c=char))
                    elif random.random() < 0.3:
                        line.append("\033[0;32m{c}\033[0m".format(c=char))
                    else:
                        line.append("\033[0;90m{c}\033[0m".format(c=char))
                else:
                    line.append(" ")

            # 随机插入十六进制块
            if random.random() < 0.05 and cols > 8:
                pos = random.randint(0, cols - 8)
                hex_block = "".join(random.choice(self.hex_chars) for _ in range(8))
                for i, c in enumerate(hex_block):
                    if pos + i < len(line):
                        line[pos + i] = "\033[1;33m{c}\033[0m".format(c=c)

            screen.append("".join(line))

        return screen

    def _generate_matrix_screen(self):
        cols = self.size.columns
        rows = self.size.rows - 2
        screen = []

        for row in range(rows):
            line = []
            for _ in range(cols):
                if random.random() < self.density * 0.8:
                    char = random.choice(self.matrix_chars + self.alphanum_chars)
                    # 根据行位置计算亮度，模拟字符下落效果
                    brightness = int((float(row) / max(1.0, float(rows))) * 10) + random.randint(0, 5)
                    if brightness > 8:
                        line.append("\033[1;32m{c}\033[0m".format(c=char))
                    elif brightness > 4:
                        line.append("\033[0;32m{c}\033[0m".format(c=char))
                    else:
                        line.append("\033[0;90m{c}\033[0m".format(c=char))
                else:
                    line.append(" ")
            screen.append("".join(line))

        return screen

    def _generate_code_screen(self):
        cols = self.size.columns
        rows = self.size.rows - 2
        screen = []

        for _ in range(rows):
            line = []
            for _ in range(cols):
                if random.random() < self.density * 0.8:
                    char = random.choice(self.code_chars + self.alphanum_chars)
                    line.append("\033[0;36m{c}\033[0m".format(c=char))
                else:
                    line.append(" ")
            screen.append("".join(line))

        code_snippets = [
            "root@{sys}:~# {cmd}".format(
                sys=random.choice(self.systems),
                cmd=random.choice(['sudo', 'python3', 'nmap', 'hydra']),
            ),
            "ACCESS: {a} | LEVEL: {lvl}".format(
                a=random.choice(['GRANTED', 'DENIED']),
                lvl=random.choice(['ROOT', 'ADMIN']),
            ),
            "ENCRYPTION: {e} | STATUS: {s}".format(
                e=random.choice(['AES-256', 'RSA-4096']),
                s=random.choice(['CRACKED', 'PENDING']),
            ),
            "IP: {a}.{b}.{c}.{d}".format(
                a=random.randint(1, 255),
                b=random.randint(1, 255),
                c=random.randint(1, 255),
                d=random.randint(1, 255),
            ),
            "TRANSFER: {g}.{m:02d} GB | SPEED: {sp} MB/s".format(
                g=random.randint(1, 999),
                m=random.randint(0, 99),
                sp=random.randint(10, 999),
            ),
        ]

        # 随机插入代码片段到屏幕中
        for _ in range(random.randint(2, min(5, max(1, rows // 3)))):
            if rows > 3 and cols > 50:
                r = random.randint(0, rows - 2)
                c = random.randint(0, max(0, cols - 50))
                snippet = random.choice(code_snippets)
                if c + len(snippet) < cols:
                    screen[r] = screen[r][:c] + "\033[1;33m{t}\033[0m".format(t=snippet) + screen[r][c + len(snippet):]

        return screen

    def _generate_glitch_screen(self):
        cols = self.size.columns
        rows = self.size.rows - 2
        screen = []

        for _ in range(rows):
            line = []
            for _ in range(cols):
                if random.random() < self.density * 0.6:
                    chars = self.glitch_chars + self.binary_chars + self.code_chars
                    char = random.choice(chars)
                    colors = [
                        '\033[0;31m', '\033[0;32m', '\033[0;33m', '\033[0;34m',
                        '\033[0;35m', '\033[0;36m', '\033[1;37m',
                    ]
                    color = random.choice(colors)
                    line.append("{color}{c}\033[0m".format(color=color, c=char))
                else:
                    line.append(" ")

            # 随机插入高亮故障块
            if random.random() < 0.1 and cols > 5:
                pos = random.randint(0, cols - 5)
                glitch = "".join(random.choice(self.glitch_chars) for _ in range(4))
                for i, c in enumerate(glitch):
                    if pos + i < len(line):
                        line[pos + i] = "\033[1;37m{c}\033[0m".format(c=c)

            screen.append("".join(line))

        return screen

    def show_completion_screen(self):
        if not self.ansi_enabled:
            print("\nOPERATION COMPLETED SUCCESSFULLY")
            print("Duration: {d}s".format(d=int(self.duration)))
            return

        cols = self.size.columns
        rows = self.size.rows
        self.terminal.clear_screen()

        lines = []
        lines.append("\033[1;32m" + "█" * cols + "\033[0m")
        lines.append("")

        title = "OPERATION COMPLETED SUCCESSFULLY"
        pad = max(0, (cols - 50) // 2)
        lines.append(" " * pad + "\033[1;36m╔══════════════════════════════════════════════╗\033[0m")
        lines.append(" " * pad + "\033[1;36m║       OPERATION COMPLETED SUCCESSFULLY       ║\033[0m")
        lines.append(" " * pad + "\033[1;36m╚══════════════════════════════════════════════╝\033[0m")
        lines.append("")

        stats = [
            "All systems penetrated: {n} targets".format(n=random.randint(5, 20)),
            "Data exfiltrated: {g}.{m:02d} GB".format(g=random.randint(100, 999), m=random.randint(0, 99)),
            "Zero-day exploits used: {n}".format(n=random.randint(1, 5)),
            "Anonymity maintained: {n}%".format(n=random.randint(95, 100)),
            "Forensic evidence: 0 bytes",
        ]
        for stat in stats:
            pad2 = max(0, (cols - 60) // 2)
            lines.append(" " * pad2 + "\033[1;33m[✓] {s}\033[0m".format(s=stat))

        lines.extend([
            "",
            " " * max(0, (cols - 70) // 2) + "\033[1;35m\"THE ONLY IMPOSSIBLE HACK IS THE ONE YOU NEVER ATTEMPT.\"",
            " " * max(0, (cols - 70) // 2) + "\033[1;35m                                   - Jiahao 2077",
            "",
            "\033[1;31m" + "█" * cols + "\033[0m",
        ])

        # 居中显示完成界面
        total = len(lines)
        start_row = max(1, (rows - total) // 2)
        self.terminal.clear_screen()
        for i, line in enumerate(lines):
            if start_row + i <= rows:
                self.terminal.move_cursor(1, start_row + i)
                sys.stdout.write(line)

        prompt = "Press Enter to return to reality..."
        self.terminal.move_cursor(max(1, (cols - len(prompt)) // 2), rows - 2)
        sys.stdout.write("\033[1;37m{p}\033[0m".format(p=prompt))
        sys.stdout.flush()
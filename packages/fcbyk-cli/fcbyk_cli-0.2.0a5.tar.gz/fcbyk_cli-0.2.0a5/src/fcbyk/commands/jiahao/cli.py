"""
jiahao 命令行接口模块

函数:
- select_mode_interactively(current: str) -> DisplayMode: 交互式选择显示模式（支持方向键/ws键）
- jiahao(duration, speed, density): CLI 主入口，启动黑客终端模拟器
"""

import sys
import time
from typing import Dict

import click

from .service import DisplayMode, HackerTerminal, enable_windows_ansi


def select_mode_interactively(current: str) -> DisplayMode:
    modes = [DisplayMode.BINARY, DisplayMode.CODE, DisplayMode.MATRIX, DisplayMode.GLITCH]
    descriptions: Dict[DisplayMode, str] = {
        DisplayMode.BINARY: 'Matrix-style binary rain',
        DisplayMode.CODE: 'Random code blocks and snippets',
        DisplayMode.MATRIX: 'Green cascade characters',
        DisplayMode.GLITCH: 'Glitch symbols and blocks',
    }

    current_mode = DisplayMode(current) if current in [m.value for m in modes] else DisplayMode.BINARY
    index = modes.index(current_mode)
    lines_to_render = len(modes) + 3

    def render() -> None:
        click.echo("\nUse ↑/↓ to choose display mode, Enter to confirm:")
        for i, m in enumerate(modes):
            selected = i == index
            pointer = "\033[1;32m> \033[0m" if selected else "  "
            color = "\033[1;37m" if selected else "\033[0;37m"
            click.echo(f"{pointer}{color}{m.value:<7}\033[0m - {descriptions[m]}")
        click.echo("")

    render()

    while True:
        ch = click.getchar()

        # 处理特殊按键序列（方向键在不同平台下的编码）
        seq = ch
        if ch in ('\x1b', '\xe0', '\x00'):
            second = click.getchar()
            third = click.getchar() if second in ('[', 'O') else ''
            seq = ch + second + third

        if seq in ('\x1b[A', '\xe0H') or seq.startswith('\x1b[A'):
            index = (index - 1) % len(modes)
        elif seq in ('\x1b[B', '\xe0P') or seq.startswith('\x1b[B'):
            index = (index + 1) % len(modes)
        elif ch in ('w', 'W'):
            index = (index - 1) % len(modes)
        elif ch in ('s', 'S'):
            index = (index + 1) % len(modes)
        elif ch in ('\r', '\n'):
            break
        else:
            continue

        # 清除之前的输出并重新渲染
        if sys.stdout.isatty():
            sys.stdout.write('\033[F' * lines_to_render)
            sys.stdout.write('\033[J')
            sys.stdout.flush()
        render()

    return modes[index]


@click.command(name='jiahao', help='Jiahao Hacker Terminal Simulator')
@click.option('--duration', '-d', default=30, type=int, help='Run duration in seconds', show_default=True)
@click.option('--speed', '-s', default=0.05, type=float, help='Refresh interval in seconds (smaller is faster)', show_default=True)
@click.option('--density', default=0.7, type=float, help='Character density 0.1-1.0', show_default=True)
def jiahao(duration: int, speed: float, density: float):
    click.clear()

    enable_windows_ansi()
    ansi_enabled = sys.stdout.isatty()

    click.echo("\n" + "=" * 80)
    click.echo("\033[1;31m[!] WARNING: Entering full-screen hacker mode\033[0m")
    click.echo("\033[1;33m[!] Press Ctrl+C to exit at any time\033[0m")
    click.echo("\033[1;32m[!] This is a visual simulation only; no real network activity will occur\033[0m")
    click.echo("=" * 80)

    mode = select_mode_interactively('binary')

    input("\033[1;35m[+] Press Enter to enter hacker mode...\033[0m")
    click.echo("\r\033[1;32m[+] Entering the Matrix...                          \033[0m")
    time.sleep(1)

    terminal = HackerTerminal(
        mode=mode,
        duration=duration,
        speed=speed,
        density=min(max(density, 0.1), 1.0),
        ansi_enabled=ansi_enabled,
    )

    try:
        terminal.run()
        terminal.show_completion_screen()
        input("")
    except Exception as e:
        click.echo(f"\n\033[1;31m[!] 错误: {e}\033[0m")
    finally:
        # 恢复光标显示
        sys.stdout.write('\033[?25h')
        sys.stdout.flush()